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

## Quick Start

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run migrations:
   ```
   alembic upgrade head
   ```

3. Make changes to the view in `views.py` and generate a new migration:
   ```
   alembic revision --autogenerate -m "update active users view"
   ```

4. Apply the new migration:
   ```
   alembic upgrade head
   ```

## Key Files

- `views.py`: Contains the view definition using PGView
- `models/models.py`: SQLAlchemy models including the view representation
- `migrations/env.py`: Configured to register views for autogeneration 