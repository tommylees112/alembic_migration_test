"""create active users view

Revision ID: 7da1fc2d9e1a
Revises: 6da1fc2d9e1a
Create Date: 2023-04-01

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "7da1fc2d9e1a"
down_revision = "6da1fc2d9e1a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a view of active users (users with at least one post)
    op.execute("""
    CREATE OR REPLACE VIEW active_users AS
    SELECT u.id, u.username, u.email, COUNT(p.id) as post_count
    FROM users u
    JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username, u.email
    HAVING COUNT(p.id) > 0;
    """)


def downgrade() -> None:
    # Drop the view
    op.execute("DROP VIEW IF EXISTS active_users;")
