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
import os
import urllib.request

import setuptools.command.build_py
from setuptools import setup

_module_path_psycopg = "sqlalchemy_rdsiam.dialects:PGDialect_psycopg2rdsiam"
_module_path_asyncpg = "sqlalchemy_rdsiam.dialects:PGDialect_asyncpgrdsiam"

_aws_rds_ca_bundle_url = (
    "https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem"
)


def _get_readme_contents() -> str:
    with open("README.md") as f:
        return f.read()


class BuildPyCommand(setuptools.command.build_py.build_py):
    """Custom build command that downloads the AWS RDS CA bundle.

    See https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html
    and details in ``README.md``.
    """

    def run(self):
        self._download_aws_rds_ca_bundle()
        setuptools.command.build_py.build_py.run(self)

    def _download_aws_rds_ca_bundle(self):
        aws_rds_ca_bundle_path = os.path.join(
            os.path.dirname(__file__),
            "sqlalchemy_rdsiam",
            "rds-ca-bundle",
            "global-bundle.pem",
        )

        os.makedirs(os.path.dirname(aws_rds_ca_bundle_path))

        print(f"Downloading AWS RDS CA bundle from {_aws_rds_ca_bundle_url}...")
        urllib.request.urlretrieve(_aws_rds_ca_bundle_url, aws_rds_ca_bundle_path)


setup(
    name="sqlalchemy-rdsiam",
    cmdclass={"build_py": BuildPyCommand},
    use_scm_version={"local_scheme": "no-local-version"},
    setup_requires=["setuptools_scm"],
    description=(
        "SQLAlchemy dialects to connect to Amazon RDS instances "
        "with IAM authentication"
    ),
    long_description=_get_readme_contents(),
    long_description_content_type="text/markdown",
    packages=["sqlalchemy_rdsiam"],
    include_package_data=True,
    python_requires=">=3.6",
    # Do not require `psycopg2` since `psycopg2-binary` can also be used.
    # Do not require `asyncpg` either, since we do not know which client
    # library will be used.
    install_requires=["SQLAlchemy>=1.3", "boto3"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "sqlalchemy.dialects": [
            f"postgresql.psycopg2rdsiam = {_module_path_psycopg}",
            f"postgresql.asyncpgrdsiam = {_module_path_asyncpg}",
        ]
    },
    options={"bdist_wheel": {"universal": True}},
    zip_safe=False,
)
