"""
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

import asyncio
import os
from unittest.mock import patch

import pytest
import sqlalchemy
from pytest_postgresql import factories

from sqlalchemy_rdsiam.dialects import _has_sqlalchemy_asyncpg

if _has_sqlalchemy_asyncpg:
    from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_rdsiam.rds import rds_client

pg_password_env = os.getenv("PGPASSWORD")

if pg_password_env:
    # Running in CI with a service container
    pg_password = pg_password_env
    pg_instance = factories.postgresql_noproc(password=pg_password)  # TODO
else:
    # Running locally, start a PostgreSQL process
    pg_password = "test-password"
    pg_instance = factories.postgresql_proc(password=pg_password)


@pytest.fixture
def mock_boto_client():
    with patch("boto3.client") as mock_boto_client:
        mock_boto_client.return_value = mock_boto_client
        mock_boto_client.generate_db_auth_token.return_value = pg_password
        rds_client.cache_clear()
        yield mock_boto_client


@pytest.fixture
def try_connect_async():
    async def _async_try_connect(url: str) -> None:
        engine = create_async_engine(url)
        async with engine.connect():
            pass

    def _try_connect(url):
        asyncio.run(_async_try_connect(url))

    return _try_connect


@pytest.fixture
def try_connect_sync():
    def _try_connect(url: str) -> None:
        engine = sqlalchemy.create_engine(url)

        with engine.connect():
            pass

    return _try_connect
