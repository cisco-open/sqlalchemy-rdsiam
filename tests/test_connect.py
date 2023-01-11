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

from sqlalchemy_rdsiam.dialects import _has_sqlalchemy_asyncpg, _has_sqlalchemy_psycopg2


@pytest.mark.parametrize(
    "try_connect_fn,engine_prefix",
    [
        pytest.param(
            "try_connect_sync",
            "postgresql+psycopg2rdsiam",
            marks=pytest.mark.skipif(
                not _has_sqlalchemy_psycopg2, reason="psycopg2 is not supported"
            ),
        ),
        pytest.param(
            "try_connect_async",
            "postgresql+asyncpgrdsiam",
            marks=pytest.mark.skipif(
                not _has_sqlalchemy_asyncpg, reason="asyncpg is not supported"
            ),
        ),
    ],
)
class TestConnectionSQLAlchemy:
    def test_connect(
        self, request, mock_boto_client, pg_instance, try_connect_fn, engine_prefix
    ):
        """Check that we can connect with default settings."""
        db_name = f"{pg_instance.dbname}_tmpl"
        try_connect = request.getfixturevalue(try_connect_fn)

        url = (
            f"{engine_prefix}://"
            f"{pg_instance.user}:@{pg_instance.host}:{pg_instance.port}/{db_name}"
        )

        try_connect(url)

        mock_boto_client.assert_called_with("rds", region_name=None)
        mock_boto_client.generate_db_auth_token.assert_called_with(
            DBHostname=pg_instance.host,
            Port=pg_instance.port,
            DBUsername=pg_instance.user,
        )

    def test_connect_region(
        self, request, mock_boto_client, pg_instance, try_connect_fn, engine_prefix
    ):
        """Check that we can connect with a custom AWS region."""
        db_name = f"{pg_instance.dbname}_tmpl"
        try_connect = request.getfixturevalue(try_connect_fn)

        url = (
            f"{engine_prefix}://"
            f"{pg_instance.user}:@{pg_instance.host}:{pg_instance.port}/{db_name}"
            "?aws_region_name=ap-central-1"
        )

        try_connect(url)

        mock_boto_client.assert_called_with("rds", region_name="ap-central-1")
        mock_boto_client.generate_db_auth_token.assert_called_with(
            DBHostname=pg_instance.host,
            Port=pg_instance.port,
            DBUsername=pg_instance.user,
        )


@pytest.mark.skipif(
    not _has_sqlalchemy_psycopg2,
    reason="psycopg2 is not supported",
)
def test_connect_without_sqla(mock_boto_client, pg_instance):
    """Check that we can connect without SQLAlchemy."""
    import sqlalchemy_rdsiam.dbapi_psycopg2 as psycopg2

    psycopg2.connect(
        user=pg_instance.user,
        host=pg_instance.host,
        port=pg_instance.port,
        database=f"{pg_instance.dbname}_tmpl",
        aws_region_name="us-east-1",
    )

    mock_boto_client.assert_called_with("rds", region_name="us-east-1")
    mock_boto_client.generate_db_auth_token.assert_called_with(
        DBHostname=pg_instance.host, Port=pg_instance.port, DBUsername=pg_instance.user
    )

    # asyncpg doesn't officially support the DBAPI interface.
