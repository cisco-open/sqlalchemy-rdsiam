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

import pytest
from sqlalchemy.exc import OperationalError

from sqlalchemy_rdsiam.dialects import _has_sqlalchemy_asyncpg, _has_sqlalchemy_psycopg2

try:
    from asyncpg.exceptions import InvalidCatalogNameError
except ImportError:
    InvalidCatalogNameError = None


@pytest.mark.parametrize(
    "try_connect_fn,engine_prefix,expected_exception,db_suffix",
    [
        pytest.param(
            "try_connect_sync",
            "postgresql+psycopg2rdsiam",
            OperationalError,
            "psycopg2",
            marks=pytest.mark.skipif(
                not _has_sqlalchemy_psycopg2, reason="psycopg2 not supported"
            ),
        ),
        pytest.param(
            "try_connect_async",
            "postgresql+asyncpgrdsiam",
            InvalidCatalogNameError,
            "asyncpg",
            marks=pytest.mark.skipif(
                not _has_sqlalchemy_asyncpg, reason="asyncpg not supported"
            ),
        ),
    ],
)
def test_create_if_not_exists(
    request,
    mock_boto_client,
    pg_instance,
    try_connect_fn,
    engine_prefix,
    expected_exception,
    db_suffix,
):
    """Check creation of the database if it doesn't exist."""
    db_name = f"{pg_instance.dbname}_{db_suffix}_doesntexist"
    try_connect = request.getfixturevalue(try_connect_fn)

    # Doesn't exist, and creation disabled by default
    base_url = (
        f"{engine_prefix}://"
        f"{pg_instance.user}:@{pg_instance.host}:{pg_instance.port}/{db_name}"
    )

    with pytest.raises(expected_exception):
        try_connect(base_url)

    # Doesn't exist, and creation disabled explicitly
    url = f"{base_url}?create_db_if_not_exists=false"

    with pytest.raises(expected_exception):
        try_connect(url)

    # Doesn't exist, and creation enabled explicitly
    url = f"{base_url}?create_db_if_not_exists=true"
    try_connect(url)

    # Database should exist now
    try_connect(base_url)
