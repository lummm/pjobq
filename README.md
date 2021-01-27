* JOBS
A DB - defined job queue ala cron.
- python process stays in sync with 'cron' table,
  and launches jobs per schedule.

- use ZeroMQ to keep python process in sync (ie. update to cron table triggers reload in py worker)

* impl
- define job schema
- define cron parser for py
- define tasks and load them (tests)
- make sync over ZeroMQ


