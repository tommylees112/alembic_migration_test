import os
import subprocess

import pytest
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

# Database connection parameters for testing
TEST_DB_NAME = "test_alembic_migrate"
TEST_DB_USER = os.environ.get("DB_USER", "postgres")
TEST_DB_PASS = os.environ.get("DB_PASS", "postgres")
TEST_DB_HOST = os.environ.get("DB_HOST", "localhost")
TEST_DB_URL = (
    f"postgresql://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}/{TEST_DB_NAME}"
)


@pytest.fixture(scope="module")
def setup_test_db():
    """Create a test database and set up environment for tests"""
    # Connect to default postgres db to create/drop test database
    admin_url = f"postgresql://{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}/postgres"
    admin_engine = sa.create_engine(admin_url)

    # Drop test database if it exists and create it fresh
    with admin_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        try:
            conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        except:
            pass
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    # Set environment variables for alembic
    os.environ["DB_NAME"] = TEST_DB_NAME
    os.environ["DB_USER"] = TEST_DB_USER
    os.environ["DB_PASS"] = TEST_DB_PASS
    os.environ["DB_HOST"] = TEST_DB_HOST

    # Return test database connection
    engine = sa.create_engine(TEST_DB_URL)
    yield engine

    # Clean up
    engine.dispose()
    with admin_engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
    admin_engine.dispose()


def run_alembic_command(command):
    """Run an alembic command using subprocess"""
    result = subprocess.run(
        f"uv run alembic {command}", shell=True, capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"Command failed: {result.stderr}")
        raise Exception(f"Alembic command failed: {result.stderr}")
    return result.stdout


def test_initial_migration(setup_test_db):
    """Test that the initial migration creates tables and views correctly"""
    engine = setup_test_db

    # Run initial migration
    run_alembic_command("upgrade head")

    # Check that tables exist
    with engine.connect() as conn:
        # Check for users table
        result = conn.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users')"
            )
        )
        assert result.scalar(), "Users table was not created"

        # Check for posts table
        result = conn.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'posts')"
            )
        )
        assert result.scalar(), "Posts table was not created"

        # Check for active_users view
        result = conn.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.views WHERE table_schema = 'public' AND table_name = 'active_users')"
            )
        )
        assert result.scalar(), "Active users view was not created"

        # Check view definition includes the expected columns
        result = conn.execute(
            text(
                "SELECT * FROM information_schema.columns WHERE table_name = 'active_users'"
            )
        )
        columns = [row[3] for row in result.fetchall()]  # Column 3 is column_name
        assert "id" in columns, "View should contain id column"
        assert "username" in columns, "View should contain username column"
        assert "post_count" in columns, "View should contain post_count column"


def test_view_change_migration(setup_test_db):
    """Test that changes to views are properly detected and migrated"""
    engine = setup_test_db

    # Run initial migration
    run_alembic_command("upgrade head")

    # Modify the view definition in views.py
    with open("alembic_migrate/views.py", "r") as f:
        original_content = f.read()

    try:
        # Add a new column to the view definition
        modified_content = original_content.replace(
            "COUNT(p.id) as post_count",
            "COUNT(p.id) as post_count, MIN(p.created_at) as first_post_date",
        )

        with open("alembic_migrate/views.py", "w") as f:
            f.write(modified_content)

        # Generate a new migration for the view change
        result = run_alembic_command(
            'revision --autogenerate -m "add first_post_date to view"'
        )
        assert "add first_post_date to view" in result, (
            "Migration should be generated with the correct message"
        )

        # Apply the migration
        run_alembic_command("upgrade head")

        # Verify the view has the new column
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT * FROM information_schema.columns WHERE table_name = 'active_users'"
                )
            )
            columns = [row[3] for row in result.fetchall()]  # Column 3 is column_name
            assert "first_post_date" in columns, (
                "View should contain the new first_post_date column"
            )

        # Test downgrade and ensure it works properly
        run_alembic_command("downgrade -1")

        # Verify the view has reverted to the original definition
        with engine.connect() as conn:
            result = conn.execute(
                text(
                    "SELECT * FROM information_schema.columns WHERE table_name = 'active_users'"
                )
            )
            columns = [row[3] for row in result.fetchall()]  # Column 3 is column_name
            assert "first_post_date" not in columns, (
                "first_post_date should not be present after downgrade"
            )

    finally:
        # Restore the original views.py
        with open("alembic_migrate/views.py", "w") as f:
            f.write(original_content)


def test_model_view_consistency(setup_test_db):
    """Test that the SQLAlchemy model stays consistent with the view"""
    engine = setup_test_db

    # Run initial migration
    run_alembic_command("upgrade head")

    # Import the model and create a session
    from alembic_migrate.models.models import ActiveUser

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Test that we can query the view through the model
        active_users = session.query(ActiveUser).all()
        # We don't expect any data, but the query should execute without errors
        assert isinstance(active_users, list), (
            "Query should return a list, even if empty"
        )

        # Insert test data to verify view content
        conn = engine.connect()
        trans = conn.begin()
        try:
            # Insert a user
            conn.execute(
                text(
                    "INSERT INTO users (id, username, email) VALUES (1, 'testuser', 'test@example.com')"
                )
            )
            # Insert a post by this user
            conn.execute(
                text(
                    "INSERT INTO posts (id, title, content, user_id) VALUES (1, 'Test Post', 'Content', 1)"
                )
            )
            trans.commit()

            # Test that the view shows the user as active
            active_users = session.query(ActiveUser).all()
            assert len(active_users) == 1, "Should find one active user"
            assert active_users[0].username == "testuser", "Username should match"
            assert active_users[0].post_count == 1, "Post count should be 1"

        except:
            trans.rollback()
            raise
        finally:
            conn.close()

    finally:
        session.close()


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
