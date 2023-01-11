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

from typing import List, Set
from unittest.mock import patch

import pytest
from cryptography.x509 import Certificate, load_pem_x509_certificate
from cryptography.x509.oid import NameOID

import sqlalchemy_rdsiam.dialects


@pytest.mark.skipif(
    not sqlalchemy_rdsiam.dialects._has_sqlalchemy_psycopg2,
    reason="psycopg2 is not supported",
)
def test_sslrootcert_psycopg2(pg_instance, try_connect_sync):
    import sqlalchemy_rdsiam.dbapi_psycopg2

    with patch(
        "sqlalchemy_rdsiam.dbapi_psycopg2._psycopg2_connect",
        wraps=sqlalchemy_rdsiam.dbapi_psycopg2._psycopg2_connect,
    ) as mock_connect:
        db_name = f"{pg_instance.dbname}_tmpl"

        url = (
            "postgresql+psycopg2rdsiam://"
            f"{pg_instance.user}:@{pg_instance.host}:{pg_instance.port}/{db_name}"
            "?rds_sslrootcert=true"
        )

        try_connect_sync(url)

        # Check the SSL root cert file that was passed to psycopg2
        certs = _read_certs(mock_connect.call_args.kwargs["sslrootcert"])
        common_names = _obj_read_common_names(certs)

        assert any(
            cn.startswith("Amazon RDS eu-central-1 Root CA") for cn in common_names
        )
        assert any(cn.startswith("Amazon RDS us-east-1 Root CA") for cn in common_names)


@pytest.mark.skipif(
    not sqlalchemy_rdsiam.dialects._has_sqlalchemy_asyncpg,
    reason="asyncpg is not supported",
)
def test_sslrootcert_asyncpg(pg_instance, try_connect_async):
    db_name = f"{pg_instance.dbname}_tmpl"

    url = (
        "postgresql+asyncpgrdsiam://"
        f"{pg_instance.user}:@{pg_instance.host}:{pg_instance.port}/{db_name}"
        "?rds_sslrootcert=true"
    )

    with patch(
        "sqlalchemy_rdsiam.dbapi_asyncpg._asyncpg_connect",
        wraps=sqlalchemy_rdsiam.dbapi_asyncpg._asyncpg_connect,
    ) as connect_fn:
        try:
            try_connect_async(url)
        except AttributeError:
            # The mocked object does not implement all required methods, but it
            # is good enough to catch the arguments to be checked
            pass

        # Check the SSL root cert file that was passed to asyncpg
        connect_fn.assert_awaited()

        assert "sslrootcert" in connect_fn.call_args.kwargs["dsn"]


def _split_bundle(pem_bytes: bytes) -> List[bytes]:
    pem_start_line = b"-----BEGIN CERTIFICATE-----"
    certs = pem_bytes.split(pem_start_line)

    # First one will be empty
    return [pem_start_line + cert for cert in certs[1:]]


def _read_certs(filename: str) -> List[Certificate]:
    with open(filename, "rb") as f:
        pem_bytes = f.read()

    pem_certs = _split_bundle(pem_bytes)

    return [load_pem_x509_certificate(pem_cert) for pem_cert in pem_certs]


def _obj_read_common_names(certs: List[Certificate]) -> Set[str]:
    return {
        attr.value
        for cert in certs
        for attr in cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    }


def _dict_read_common_names_(certs):
    names = []
    for c in certs:
        data = c["subject"]
        for d in data:
            k, v = d[0]
            if k == "commonName":
                names.append(v)
    return names
