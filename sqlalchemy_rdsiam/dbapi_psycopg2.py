"""DBAPI-compatible module that wraps ``psycopg2``.

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
import re
from typing import Any, Callable, Optional

import psycopg2
import sqlalchemy.exc

# Explicitly import what we use below
# Import the rest of the API
from psycopg2 import *  # noqa: F403,F401
from psycopg2 import OperationalError, sql
from psycopg2.extensions import connection

from sqlalchemy_rdsiam.build import build_connect_kwargs

_psycopg2_connect = psycopg2.connect
_logger = logging.getLogger(__name__)


def connect(dsn: Optional[str] = None, **kwargs: Any) -> connection:
    """Wrap ``psycopg2.connect`` to support RDS IAM
    authentication, and automatic database creation.
    """
    if dsn is not None:
        # Although this DBAPI interface can be used directly, our
        # focus is on SQLAlchemy, which always transforms DSNs
        # into keyword arguments first using `Dialect.create_connect_args`.
        raise ValueError(
            "Arguments should be passed as keyword arguments: "
            "libpq DSNs are not supported"
        )

    create_db_if_not_exists = (
        kwargs.get("create_db_if_not_exists", "").lower() == "true"
    )

    kwargs = build_connect_kwargs(kwargs)

    # 'database' is a deprecated alias still used by SQLAlchemy 1.4.
    if "database" in kwargs:
        kwargs["dbname"] = kwargs.pop("database")

    try:
        conn = _psycopg2_connect(**kwargs)

    except (psycopg2.OperationalError, sqlalchemy.exc.OperationalError) as exc:
        # We could check explicitly if the database exists before trying to
        # connect to it. However, this introduces overhead for what should
        # be a rare situation. Instead, we optimistically assume that the
        # database exists, and only create it if the connection fails.
        if not create_db_if_not_exists or not _is_database_does_not_exist(exc):
            raise

        _logger.info(
            f"Creating database '{kwargs['dbname']}' on instance"
            f" '{kwargs['host']}:{kwargs['port']}'"
        )
        _create_database(_psycopg2_connect, **kwargs)

        # Attempt to connect again now that database has been created
        conn = _psycopg2_connect(**kwargs)

    return conn


def _is_database_does_not_exist(exception: OperationalError) -> bool:
    """Check if the exception is about the database not existing."""
    msg = str(exception)
    return bool(re.search(r"database \"[^\"]+\" does not exist", msg))


def _create_database(connect_fn: Callable, **kwargs: Any) -> None:
    """Create the database."""
    kwargs_postgres = {**kwargs, **{"dbname": "postgres"}}

    conn = connect_fn(**kwargs_postgres)
    conn.autocommit = True

    query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(kwargs["dbname"]))

    try:
        cursor = conn.cursor()
        cursor.execute(query)

    finally:
        conn.close()
