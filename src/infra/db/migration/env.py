from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from get_config import get_key_config
from src.infra.db.migration import model

db_dsn = get_key_config("DB_CONNECTION")

config = context.config


if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = [model.metadata]
try:
    url = config.cmd_opts.pg_url
except AttributeError:
    url = db_dsn


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
