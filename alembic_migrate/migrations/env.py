import os
import sys
from logging.config import fileConfig

import dotenv
from alembic import context
from sqlalchemy import engine_from_config, pool

# Load .env file
dotenv.load_dotenv()

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Inject environment variables for database connection
section = config.config_ini_section
config.set_section_option(section, "DB_USER", os.getenv("DB_USER", "tommy"))
config.set_section_option(section, "DB_PASS", os.getenv("DB_PASS", "1234"))
config.set_section_option(section, "DB_NAME", os.getenv("DB_NAME", "alembic_migrate"))
config.set_section_option(section, "DB_HOST", os.getenv("DB_HOST", "localhost"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from alembic_migrate.models import Base

target_metadata = Base.metadata

# Register alembic_utils entities for autogeneration
from alembic_utils.replaceable_entity import register_entities

from alembic_migrate.views import active_users_view

register_entities([active_users_view])

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
