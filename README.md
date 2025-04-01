# Analytics View Migration with Alembic

## The Problem: Database View Drift

At FastGrowth Inc., our analytics team relies heavily on database views to generate real-time reports. As the company scaled, we faced a growing challenge:

**The View Drift Problem:** Our database views were created and modified directly in production by different team members. No one tracked these changes in version control, leading to:

1. **Silent failures** when application code expected columns that had been renamed or removed
2. **Deployment headaches** when moving from development to staging to production
3. **Documentation gaps** where no one knew why a view was structured a certain way
4. **Environment inconsistencies** between dev, test, and production databases

When our monthly executive dashboard broke after an untracked view change, it became clear we needed a solution.

## The Solution: Version-Controlled Views with Alembic

This project demonstrates our solution: using Alembic with alembic_utils to version control database views the same way we track table schemas.

With this approach:
- Views are defined in code, not created ad-hoc in the database
- View changes are automatically detected and migrated
- All database objects (tables AND views) follow the same migration workflow
- Rollbacks are possible when view changes cause issues

## How It Works

We use a simple user-posts database to demonstrate the approach. The `active_users` view shows users who have created at least one post, along with their activity metrics.

Instead of manually writing migrations for views, we define them once using `alembic_utils.PGView` and let the migration tools handle the rest.

---

## Project Setup

- SQLAlchemy ORM models for `User` and `Post` tables
- An `active_users` view that reports user activity metrics
- Alembic migrations with alembic_utils integration

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your database connection in `.env` or use environment variables (see `alembic.ini`)

3. Run migrations:
   ```
   alembic upgrade head
   ```

4. Generate new migrations after changes:
   ```
   alembic revision --autogenerate -m "your message"
   ```

## Migrating Database Views

With `alembic_utils`, database views are now managed automatically:

1. Define your view in `views.py` using `PGView`
2. Update the corresponding SQLAlchemy model in `models.py` if needed
3. Run `alembic revision --autogenerate` to generate the migration
4. Apply with `alembic upgrade head`

The migration will include proper CREATE, DROP, or REPLACE operations for your views.