"""DBAPI-compatible module that wraps the SQLAlchemy adapter for
``asyncpg``.

Copyright 2022 Cisco Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging
from typing import Any, Callable, Optional
from urllib.parse import urlencode

import asyncpg

# Import the rest of the API
from asyncpg import *  # noqa: F403,F401

from sqlalchemy_rdsiam.build import build_connect_kwargs

_logger = logging.getLogger(__name__)
_asyncpg_connect = asyncpg.connect


async def connect(
    dsn: Optional[str] = None, **kwargs: Any
) -> asyncpg.connection.Connection:
    if dsn is not None:
        raise ValueError(
            "Arguments should be passed as keyword arguments: " "DSNs are not supported"
        )

    create_db_if_not_exists = (
        kwargs.get("create_db_if_not_exists", "").lower() == "true"
    )

    kwargs = build_connect_kwargs(kwargs)

    # asyncpg's keyword arguments do not follow the PostgreSQL naming
    # as psycopg2 does. Instead, asyncpg has logic in the DSN parsing
    # code to map from a PostgreSQL DSN to the right asyncpg keyword
    # arguments. Hence, we build a DSN to leverage that logic.

    # Arguments supported by `asyncpg.connect`
    kwargs_keys = {"host", "port", "user", "password", "database"}

    # Arguments to pass directly to `async.connect` as keyword arguments
    direct_kwargs = {k: v for k, v in kwargs.items() if k in kwargs_keys}

    # Arguments to pass to `async.connect` through `dsn`
    dsn_kwargs = {k: v for k, v in kwargs.items() if k not in kwargs_keys}

    query = urlencode(dsn_kwargs)
    dsn = f"postgres:///?{query}"

    # Final argument set
    kwargs = {
        "dsn": dsn,
        **direct_kwargs,
    }

    try:
        return await _asyncpg_connect(**kwargs)

    except asyncpg.exceptions.InvalidCatalogNameError:
        # We could check explicitly if the database exists before trying to
        # connect to it. However, this introduces overhead for what should
        # be a rare situation. Instead, we optimistically assume that the
        # database exists, and only create it if the connection fails.
        if not create_db_if_not_exists:
            raise

        _logger.info(
            f"Creating database '{kwargs['database']}' on instance"
            f" '{kwargs['host']}:{kwargs['port']}'"
        )

        await _create_database(_asyncpg_connect, **kwargs)

        # Attempt to connect again now that database has been created
        return await _asyncpg_connect(**kwargs)


async def _create_database(connect_fn: Callable, **kwargs: Any) -> None:
    """Create the database."""
    kwargs_postgres = {**kwargs, **{"database": "postgres"}}

    conn = await connect_fn(**kwargs_postgres)
    query = "CREATE DATABASE {}".format(asyncpg.utils._quote_ident(kwargs["database"]))

    try:
        await conn.execute(query)

    finally:
        await conn.close()
