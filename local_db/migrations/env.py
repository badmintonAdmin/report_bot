import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import pool
from alembic import context


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async connection."""
    from sqlalchemy.ext.asyncio import AsyncEngine

    engine = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        echo=True,
        poolclass=pool.NullPool,
    )

    async with engine.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn, target_metadata=target_metadata
            )
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
