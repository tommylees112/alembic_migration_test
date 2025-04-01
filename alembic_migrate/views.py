from alembic_utils.pg_view import PGView

# Define the analytics view using PGView for autogeneration
active_users_view = PGView(
    schema="public",
    signature="active_users",
    definition="""
    SELECT 
        u.id, 
        u.username, 
        u.email, 
        COUNT(p.id) as post_count,
        MAX(p.created_at) as last_post_date
    FROM users u
    JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username, u.email
    HAVING COUNT(p.id) > 0
    """,
)
