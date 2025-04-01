# Analytics View Migration with Alembic

## The Problem: Database View Drift

At FastGrowth Inc., our analytics team relies heavily on database views to generate real-time reports. As the company scaled, we faced a growing challenge:

**The View Drift Problem:** Our database views were created and modified directly in production by different team members. No one tracked these changes in version control, leading to:

1. **Silent failures** when application code expected columns that had been renamed or removed
2. **Deployment headaches** when moving from development to staging to production
3. **Documentation gaps** where no one knew why a view was structured a certain way
4. **Environment inconsistencies** between dev, test, and production databases

When our monthly executive dashboard broke after an untracked view change, it became clear we needed a solution.

## Our Journey: From Manual Migrations to alembic_utils

Initially, we tried using Alembic's standard migration approach:

```python
def upgrade():
    op.execute("""
    CREATE OR REPLACE VIEW active_users AS
    SELECT u.id, u.username, COUNT(p.id) as post_count
    FROM users u
    JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username;
    """)
```

This approach worked for creating views, but we quickly hit several problems:

1. **PostgreSQL View Limitations**: When trying to remove columns in downgrade operations, we encountered the notorious `cannot drop columns from view` error.
2. **Manual Migration Tedium**: Every view change required manually writing both upgrade and downgrade SQL.
3. **Inconsistency Risk**: Our SQLAlchemy models could easily get out of sync with the actual database views.
4. **No Autogeneration**: Alembic couldn't detect view changes automatically like it does with tables.

After a particularly painful deployment where a rollback failed due to view inconsistencies, we discovered alembic_utils.

## The Solution: Version-Controlled Views with alembic_utils

This project demonstrates our improved solution: using Alembic with alembic_utils to version control database views the same way we track table schemas.

With this approach:
- Views are defined in code, not created ad-hoc in the database
- View changes are automatically detected and migrated
- All database objects (tables AND views) follow the same migration workflow
- Rollbacks are reliable since alembic_utils handles the proper DROP and CREATE sequence

## How It Works

We use a simple user-posts database to demonstrate the approach. The `active_users` view shows users who have created at least one post, along with their activity metrics.

Instead of manually writing migrations for views, we define them once using `alembic_utils.PGView` and let the migration tools handle the rest:

```python
from alembic_utils.pg_view import PGView

active_users_view = PGView(
    schema="public",
    signature="active_users",
    definition="""
    SELECT u.id, u.username, COUNT(p.id) as post_count
    FROM users u
    JOIN posts p ON u.id = p.user_id
    GROUP BY u.id, u.username
    """
)
```

---

## Project Setup

- SQLAlchemy ORM models for `User` and `Post` tables
- An `active_users` view that reports user activity metrics
- Alembic migrations with alembic_utils integration

## Getting Started

1. Install dependencies:
   ```
   uv sync
   ```

2. Set up your database connection in `.env` or use environment variables (see `alembic.ini`)

3. Run migrations:
   ```
   uv run alembic upgrade head
   ```

4. Generate new migrations after changes:
   ```
   uv run alembic revision --autogenerate -m "your message"
   ```

## Migrating Database Views

With `alembic_utils`, database views are now managed automatically:

1. Define your view in `views.py` using `PGView`
2. Update the corresponding SQLAlchemy model in `models.py` if needed
3. Run `uv run alembic revision --autogenerate` to generate the migration
4. Apply with `uv run alembic upgrade head`

The migration will include proper CREATE, DROP, or REPLACE operations for your views.

## Test Scenario Story

Our tests simulate a real-world scenario that our analytics team faced:

### Day 1: Initial Analytics Setup

Sarah, a data engineer, sets up the initial database schema:
- A `users` table to track user information (id, username, email)
- A `posts` table to store blog content (id, title, content, user_id, created_at)

She also creates the first analytics view called `active_users` which shows users who have created at least one post, along with their post count. This view powers the company's "Active Contributors" dashboard that executives check daily.

The test `test_initial_migration` verifies this initial setup works correctly.

### Day 30: New Analytics Requirement

The product team requests a new metric: "When did users first become active?" They need to know the date of each user's first post.

Michael, another data engineer, adds a `first_post_date` column to the view:

```sql
CREATE OR REPLACE VIEW active_users AS
SELECT u.id, u.username, COUNT(p.id) as post_count, 
       MIN(p.created_at) as first_post_date
FROM users u
JOIN posts p ON u.id = p.user_id
GROUP BY u.id, u.username;
```

With alembic_utils, Michael simply updates the view definition in `views.py` and runs an autogenerate command. The migration is created and applied automatically.

The test `test_view_change_migration` simulates this change, verifying that:
1. The change is detected automatically
2. A migration is generated with the correct view definition 
3. The new column appears in the view

### Day 31: Rollback Needed

After deploying the updated view, the product team discovers a bug in the dashboard code that expects the old view structure. They need to roll back immediately.

With alembic_utils, rolling back is simple:
```
uv run alembic downgrade -1
```

This correctly drops and recreates the view with its original definition, without the "cannot drop columns from view" error that plagued our manual approach.

The test verifies that after downgrade, the `first_post_date` column is correctly removed.

### Day 32: Application Integration

Once the dashboard code is fixed, the team redeploys the updated view and confirms that the SQLAlchemy model works correctly with it.

The test `test_model_view_consistency` verifies that:
1. The SQLAlchemy model correctly maps to the view
2. When a user creates a post, they appear in the active_users view
3. The statistics (post count) are calculated correctly

This test ensures that our application code will work seamlessly with the database view through the ORM.

## Testing

We've added comprehensive tests to verify our migration approach works correctly. The tests ensure:

1. Initial migrations properly create tables and views
2. View changes are correctly detected and migrated with alembic_utils
3. Downgrade operations work properly (thanks to alembic_utils handling the DROP and CREATE)
4. SQLAlchemy models stay consistent with the database views

To run the tests:

```
uv run pytest test_migrations.py -v
```

These tests create a dedicated test database, run the migrations, verify the database objects, and then clean up. They also test that view changes are properly detected when updating the `views.py` file and that rollbacks work correctly.