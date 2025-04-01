# test_view.py
from alembic_migrate.models import SessionLocal
from alembic_migrate.models.models import ActiveUser


def test_view():
    db = SessionLocal()
    try:
        # Query active users
        active_users = db.query(ActiveUser).all()

        # Display results
        print(f"Found {len(active_users)} active users:")
        for user in active_users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Post Count: {user.post_count}")
            print(f"Last Post Date: {user.last_post_date}")
            print("-" * 30)

        return len(active_users) > 0
    finally:
        db.close()


if __name__ == "__main__":
    success = test_view()
    print(f"Test {'passed' if success else 'failed'}")
