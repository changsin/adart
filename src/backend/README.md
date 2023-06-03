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

## To migrate DB
The backend uses SQLAlechemy as the ORM and postgress as the DB.
To make any changes in the DB, you need to modify the models and schemas.
Then apply the changes through Alembic. Follow these steps to do so:

1. Make changes in app/models and app/schemas for appropriate tables
2. Inside the backend docker container, run:
```commandline
>alembic revision --autogenerate -m "message about the changes"
```
This will generate an automatically generated revision python module
that contains two functions: upgrade and downgrade.

3. Apply the changes by running:
```commandline
>alembci upgrade <revision id>
```
4. Check the DB changes in the DB docker.

### Behind the scenes
Alembic keeps track of the revisions applied to the DB in two places

1. History table:
```commandline
root@4f1e130eb92b:/app# alembic history
c4b798925338 -> 346d97176cde (head), Add columns data_labels, etc. to project
b1fe564ba4a9 -> c4b798925338, add reviewer and inspector
70393e6dbdbd -> b1fe564ba4a9, Set default value to state_id of Project
40f23ea4e3af -> 70393e6dbdbd, Add Column state_id to Project table
```

2. DB:
Inside the DB docker, you will see a table named "alembic" in the "app" database.
It has just a single entry:
```commandline
app=# select * from "alembic_version";
 version_num  
--------------
 346d97176cde
(1 row)
```

This tells you what the current version is. Based on the version number,
Alembic knows how to apply the migration version scripts in the correct order.


# 2. Backend
To access the Swagger UI of Rest API, open the page

http://[local IP address]/docs

Replace [local IP address] with the actual IP address: e.g., http://192.168.45.238/docs