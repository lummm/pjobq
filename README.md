# About
pjobq is a python library to define a dynamic job scheduler, in conjunction with postgres.

# Components

cron-style scheduler:
Define the DB table [cron_job](db/cron_job.sql) and corresponding functions to create recurring jobs with cron syntax.


# Usage
## Building
Docker image 'pjoqb' can be built from the root directory with `./hooks/build`.

python package 'pjobq' can be installed with `python -m pip install .`
