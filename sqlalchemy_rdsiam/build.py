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

from typing import Any, Dict

from sqlalchemy_rdsiam.rds import rds_client
from sqlalchemy_rdsiam.sslrootcert import sslrootcert_path


def build_connect_kwargs(kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """Build keyword arguments for the connect functions"""
    hostname = kwargs.get("host", "localhost")
    port = kwargs.get("port", 5432)
    user = kwargs.get("user", "postgres")

    rds_sslrootcert = kwargs.get("rds_sslrootcert", "").lower() == "true"

    if rds_sslrootcert:
        ssl_kwargs = {"sslrootcert": sslrootcert_path()}
    else:
        ssl_kwargs = {}

    # Optional region name. Otherwise, we will let `boto3`
    # pick out a default region from the environment.
    aws_region_name = kwargs.get("aws_region_name")
    rds_clnt = rds_client(aws_region_name)

    # Set a password based on a RDS IAM authentication token.
    # If any password was set in`kwargs`, it will be ignored
    # and overwritten.
    token = rds_clnt.generate_db_auth_token(
        DBHostname=hostname,
        Port=port,
        DBUsername=user,
    )

    token_kwargs = {"password": token}

    # Strip custom arguments
    custom_args = {"aws_region_name", "create_db_if_not_exists", "rds_sslrootcert"}
    orig_kwargs = {k: v for k, v in kwargs.items() if k not in custom_args}

    return {
        **orig_kwargs,
        **ssl_kwargs,
        **token_kwargs,
    }
