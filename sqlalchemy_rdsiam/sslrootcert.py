"""Utilities to set up the SSL root certificate(s) for connecting to RDS.

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


def sslrootcert_path() -> str:
    """Path of the global certificate bundle for all RDS regions."""
    # `importlib.resources` might be cleaner, but it is
    # not available in Python 3.6.
    module_dir = os.path.dirname(__file__)

    return os.path.join(module_dir, "rds-ca-bundle", "global-bundle.pem")
