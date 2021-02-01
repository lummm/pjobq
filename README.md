# About
pjobq is a python library to define a dynamic job scheduler, in conjunction with postgres.

# Components

The DB table *cron_job* is defined to create recurring jobs with cron syntax.
The DB table *adhoc_job* is defined to create one-time jobs with a specific timestamp.
These tables, as well as related functions, are created by the application: see [sql.py](pjobq/db/sql.py).


# Usage
## Building
Docker image 'pjobq' can be built from the root directory with `./hooks/build`.

python package 'pjobq' can be installed with `python -m pip install .`

## Running in your project
This project comes with two parts, some database definitions to load in postgres, and a python process to run that will manage jobs.
See [test setup](testing/docker-compose.yaml) for an example system.


# Requirements
postgres - with uuid-ossp:
`CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
AWS postgres supports "uuid-ossp", and this is generally my target host.  This dependency could be worked around if extension installation is a problem.

python - see [requirements.txt](requirements.txt).

# More details
See [architecture](notes/architecture.md).
