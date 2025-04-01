"""update active users view

Revision ID: 9fc4d2e0b71c
Revises: 7da1fc2d9e1a
Create Date: 2023-04-01

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "9fc4d2e0b71c"
down_revision = "7da1fc2d9e1a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Modify the view to include a last_post_date column
    op.execute("""
    CREATE OR REPLACE VIEW active_users AS
    SELECT u.id, u.username, u.email, COUNT(p.id) as post_count,
           MAX(p.created_at) as last_post_date
    FROM users u
    JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username, u.email
    HAVING COUNT(p.id) > 0;
    """)


def downgrade() -> None:
    # Revert to the previous view definition
    op.execute("""
    CREATE OR REPLACE VIEW active_users AS
    SELECT u.id, u.username, u.email, COUNT(p.id) as post_count
    FROM users u
    JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username, u.email
    HAVING COUNT(p.id) > 0;
    """)
