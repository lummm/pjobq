# About
pjobq is a python library to define a dynamic job scheduler, in conjunction with postgres.

# Components

cron-style scheduler:
Define the DB table [cron_job](db/cron_job.sql) and corresponding functions to create recurring jobs with cron syntax.


# Usage
## Building
Docker image 'pjoqb' can be built from the root directory with `./hooks/build`.

python package 'pjobq' can be installed with `python -m pip install .`

## Running in your project
This project comes with two parts, some database definitions to load in postgres, and a python process to run that will manage jobs.
See [test setup](testing/docker-compose.yaml) for an example system.


# Requirements
postgres - with uuid-ossp:
`CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
AWS postgres supports "uuid-ossp", and this is generally my target host.  This dependency could be worked around if extension installation is a problem.

python - see [requirements.txt](requirements.txt).
