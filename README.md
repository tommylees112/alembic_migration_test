# Database View Migration with Alembic

This project demonstrates how to manage PostgreSQL database views with Alembic migrations.

## Setup

1. Install dependencies:
```
uv sync
```

2. Update database connection in `alembic_migrate/models/__init__.py`

3. Create initial database tables:
```
cd alembic_migrate
PYTHONPATH=.. uv run alembic upgrade head
```

## Managing Database Views with Alembic

### Creating a new view

1. Create a new migration file:
```
uv run alembic revision -m "create new view"
```

2. Edit the file to add view creation:
```python
def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE VIEW my_view AS
    SELECT ...
    FROM ...
    """)

def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS my_view;")
```

3. Add a corresponding SQLAlchemy model:
```python
class MyView(Base):
    __tablename__ = "my_view"
    __table_args__ = {'info': {'is_view': True}}
    
    # Define columns matching your view
    id = Column(Integer, primary_key=True)
    # ... other columns
```

4. Apply the migration:
```
PYTHONPATH=.. uv run alembic upgrade head
```

### Modifying an existing view

1. Create a new migration file:
```
uv run alembic revision -m "update existing view"
```

2. Edit the file to update the view:
```python
def upgrade() -> None:
    op.execute("""
    CREATE OR REPLACE VIEW my_view AS
    SELECT ...
    FROM ...
    """)

def downgrade() -> None:
    # Previous view definition
    op.execute("""
    CREATE OR REPLACE VIEW my_view AS
    SELECT ...
    FROM ...
    """)
```

3. Update the corresponding SQLAlchemy model with any new columns.

4. Apply the migration:
```
PYTHONPATH=.. uv run alembic upgrade head
```

## Important Notes

1. Views are not detected by Alembic's autogenerate feature. You must manually create migration scripts for views.

2. When using `__table_args__ = {'info': {'is_view': True}}`, SQLAlchemy won't try to create or drop the view during metadata operations.

3. PostgreSQL views are automatically updated when underlying tables change, but column names and types must be maintained.

## Testing Your Views

After applying migrations, test your views:

```
# Connect to database
psql alembic_migrate

# List all tables and views
\dt+
\dv+

# Check view definition
\d+ my_view_name

# Query the view
SELECT * FROM my_view_name;
```

## Complete Example

Here's a complete example to test if your setup is working correctly:

### 1. Check migration status
```bash
# Should show the latest migration
uv run alembic current
```

### 2. Insert test data
```bash
# Insert a test user
psql alembic_migrate -c "INSERT INTO users (username, email) VALUES ('testuser', 'test@example.com');"

# Insert a post for this user
psql alembic_migrate -c "INSERT INTO posts (title, content, user_id) VALUES ('First Post', 'This is content', 1);"
```

### 3. Query the view
```bash
# This should show the active user with their post count and last post date
psql alembic_migrate -c "SELECT * FROM active_users;"
```

### 4. Create a Python script to query the view
Create a file named `test_view.py`:

```python
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
```

Run the test:
```bash
PYTHONPATH=. uv run test_view.py
```

### 5. Test downgrade and upgrade
```bash
# Downgrade to remove the view
uv run alembic downgrade 6da1fc2d9e1a

# Verify view is gone
psql alembic_migrate -c "\dv"

# Upgrade again to recreate the view
uv run alembic upgrade head

# Verify view is back
psql alembic_migrate -c "\dv"
```
