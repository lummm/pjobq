# About
pjobq is a python library to define a dynamic job scheduler, in conjunction with postgres.

# Specifically
We manage two styles of jobs - 'cron' jobs scheduled with cron syntax, and arbitrary timestamp 'adhoc' jobs.

# Components

The DB table *cron_job* is defined to create recurring jobs with cron syntax.
The DB table *adhoc_job* is defined to create one-time jobs with a specific timestamp.
These tables, as well as related functions, are created by the application: see [sql.py](pjobq/db/sql.py).


# Usage
## Jobs
Job creation is intended to be through the database, using the functions defined in [sql.py](pjobq/db/sql.py).
pjobq will take care of running jobs as long as it is running and connected to the db.

We expose a simple interface to define job execution - jobs have a `cmd_type` and a `cmd_payload`.
The `cmd_payload` is interpreted differently depending on the `cmd_type`.

Currently we only support `cmd_type == 'HTTP'`, although the intent is to add support for 'SQL' and 'ZMQ' jobs.

See [Job Definitions](notes/job_definitions.md) for exact definitions of job formats.

## Building
Docker image 'pjobq' can be built from the root directory with `./hooks/build`.

python package 'pjobq' can be installed with `python -m pip install .`

## Running in your project
Run a (single) process with pjobq, whether in a docker container or directly through [main.py](main.py).
DB configuration is done with environment variables, as well as log level.
For default environment variables, see [env.py](pjobq/env.py).

See [test setup](integration/docker-compose.yaml) for an example system.

# Requirements
postgres - with uuid-ossp:
`CREATE EXTENSION IF NOT EXISTS "uuid-ossp";`
AWS postgres supports "uuid-ossp" as of the time of writing.

python - see [requirements.txt](requirements.txt).

# Limitations
The scheduler is not incredibly precise, meaning a job will be run somewhere in the range
of a tenth of a second after it is scheduled.
Greater precision is not a design goal at this time.

# More details
See [architecture](notes/architecture.md).
