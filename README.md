# `sqlalchemy-rdsiam`

SQLAlchemy dialect to connect to Amazon RDS instances with IAM authentication.

The following are supported:

- Amazon RDS PostgreSQL, with `psycopg2`.
- Amazon RDS PostgreSQL, with `asyncpg`.

SQLAlchemy 1.3, 1.4 and 2.0 are supported.

## Background

Amazon RDS is managed database service on AWS, which provides the ability
to connect to database instances with
[IAM authentication](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.html)
instead of passwords. AWS SDKs or the AWS CLI can be used to generate a
connection token, valid for 15 minutes, and based on an Amazon IAM identity.

With SQLAlchemy, it is possible to use IAM authentication using one of the
following options:

- Using an event handler and the
  [`do_connect` event](https://docs.sqlalchemy.org/en/14/core/engines.html#generating-dynamic-authentication-tokens).
- Using a
  [custom connection factory](https://docs.sqlalchemy.org/en/14/core/engines.html#use-the-connect-args-dictionary-parameter).

Both options require modifying the codebase to either inject the event handler or
the custom connection factory. With many open-source tools, this requires
maintaining a fork. This repository provides a set of _dialects_ which can be
installed and used directly in any SQLAlchemy codebase instead.

## Getting Started

- Install the Python package:

  ```sh
  pip install sqlalchemy-rdsiam
  ```

- Use a connection string with scheme corresponding to the target PostgreSQL library, and
  leave out the password. For instance:

  ```sh
  postgresql+psycopg2rdsiam://username@host/dbname
  postgresql+asyncpgrdsiam://username@host/dbname
  ```

  > **Note**: if a password is provided, it will be ignored.

- Run with an IAM identity that has IAM permissions to connect to the database.
  See
  [IAM authentication](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.IAMDBAuth.Connecting.html).

## Additional Configuration

### AWS Region

The default region in the environment is used. To access a database in a
different region without changing your environment, pass the query parameter
`aws_region_name` in the connection string:

```sh
postgresql+psycopg2rdsiam://username@host/dbname?aws_region_name=us-east-2
```

### Creating the Database If It Doesn't Exists

The dialect supports optionally creating the database upon connection if it
doesn't exist. This is disabled by default. To create the database if it doesn't
exist, set the query parameter `create_db_if_not_exists` to `true`:

```sh
postgresql+psycopg2rdsiam://username@host/dbname?create_db_if_not_exists=true
```

> **Note**: the role used must have permissions to create databases.

### Set `sslrootcert` to the Amazon RDS Certificate Bundle

[Amazon RDS TLS certificates](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html)
are signed by Amazon certificate authorities, and the `sslrootcert` PostgreSQL
argument must be used in order to verify the certificate chain when connecting
to the instance. In some cases, it can be useful to directly get the CA bundle
along with the package for testing, or to streaming provisioning. To this end,
the CA bundle is automatically downloaded when installing the Python package,
and you can opt-in to use it directly.

> **Note**: make sure this is in line with your **security posture requirements**
> first.

The package can directly set `sslrootcert` to the certificate bundle for all
Amazon RDS regions. This is disabled by default. To do so, set the query
parameter `rds_sslrootcert` to `true`:

```sh
postgresql+psycopg2rdsiam://username@host/dbname?rds_sslrootcert=true
```

You still need to set `sslmode` - for instance, with `sslmode=verify-full`:

```sh
postgresql+psycopg2rdsiam://username@host/dbname?rds_sslrootcert=true&sslmode=verify-full
```

See [SSL Support](https://www.postgresql.org/docs/current/libpq-ssl.html)
for additional details.

## Contributing

See [Contributing](CONTRIBUTING.md).

## License

See [License](LICENSE).
