# Adart Backend
Adart backend is adapted from [full-stack-fastapi-postgresql](https://github.com/tiangolo/full-stack-fastapi-postgresql).
This is a bare minimum DB and backend for user and project management.

There are three components:
1. db: postgres DB
2. backend: sqlalchemy ORM for the DB
3. pgadmin: to administer DB through PGAdmin web UI

# 1. To developers
To build and run

```commandline
>docker compose up --build -d
```

To shutdown
```commandline
>docker compose down
```

## DB
1. To connect DB from outside:
Open the connection and the port

1. find hba_file
```commandline
> sudo -u postgres psql -c "show hba_file;"
```

2. Add an entry that allows remote connections to the database. For example, to allow connections from any IP address, add the following line to pg_hba.conf:

```commandline
host    all             all             0.0.0.0/0               md5
```
3. This allows any IP address to connect to any database with any user, and requires a password for authentication.
Edit the postgresql.conf file to listen on all IP addresses. By default, PostgreSQL only listens on the loopback interface. You can change this by setting the listen_addresses parameter in postgresql.conf to '*'.

```commandline
listen_addresses = '*'
```

4. Restart the PostgreSQL service to apply the changes:

```commandline
sudo service postgresql restart
```

NB. Inside a docker, hba_file, etc. are located in 

```commandline
>cd /var/lib/postgresql/data/pgdata
```