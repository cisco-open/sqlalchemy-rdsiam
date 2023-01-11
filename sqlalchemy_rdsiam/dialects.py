"""SQLAlchemy dialects for PostgreSQL that support IAM auth.

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
from types import ModuleType
from typing import Type

# Dialect for `psycopg2`, when available
try:
    # The dialect is available even if `psycopg2` is not installed.
    # Make sure it is installed first.
    import psycopg2  # noqa
    from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2

    _has_sqlalchemy_psycopg2 = True

    class PGDialect_psycopg2rdsiam(PGDialect_psycopg2):
        @classmethod
        def dbapi(cls: Type) -> ModuleType:
            return cls.import_dbapi()

        @classmethod
        def import_dbapi(cls: Type) -> ModuleType:
            from sqlalchemy_rdsiam import dbapi_psycopg2

            return dbapi_psycopg2

except ImportError:
    _has_sqlalchemy_psycopg2 = False

    class PGDialect_psycopg2rdsiam:  # type: ignore
        @classmethod
        def dbapi(cls: Type) -> ModuleType:
            return cls.import_dbapi()

        @classmethod
        def import_dbapi(cls: Type) -> ModuleType:
            raise NotImplementedError(
                """
                `psycopg2` is required to use `postgresql+psycopg2rdsiam`.
            """
            )


# Dialect for `asyncpg`, when available
try:
    # The dialect is available even if `asyncpg` is not installed.
    # Make sure it is installed first.
    import asyncpg  # noqa
    from sqlalchemy.dialects.postgresql.asyncpg import PGDialect_asyncpg

    _has_sqlalchemy_asyncpg = True

    class PGDialect_asyncpgrdsiam(PGDialect_asyncpg):
        @classmethod
        def dbapi(cls: Type) -> ModuleType:
            return cls.import_dbapi()

        @classmethod
        def import_dbapi(cls: Type) -> ModuleType:
            from sqlalchemy.dialects.postgresql.asyncpg import AsyncAdapt_asyncpg_dbapi

            from sqlalchemy_rdsiam import dbapi_asyncpg

            return AsyncAdapt_asyncpg_dbapi(asyncpg=dbapi_asyncpg)

except ImportError:
    _has_sqlalchemy_asyncpg = False

    class PGDialect_asyncpgrdsiam:  # type: ignore
        @classmethod
        def dbapi(cls: Type) -> ModuleType:
            return cls.import_dbapi()

        @classmethod
        def import_dbapi(cls: Type) -> ModuleType:
            raise NotImplementedError(
                """
                `asyncpg` is required to use `postgresql+asyncpgrdsiam`.
            """
            )
