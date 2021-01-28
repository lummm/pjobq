* JOBS
A DB - defined job queue ala cron.
- python process stays in sync with 'cron' table,
  and launches jobs per schedule.

- use ZeroMQ to keep python process in sync (ie. update to cron table triggers reload in py worker)

* impl
- define job schema
- define cron parser for py
- test pg_notify
- define tasks and load them (tests)
- define db function to schedule a recurring daily job,
  with TZ and hours:mins


* next steps
- failure notifications
- uptime notifications
  (ie. always hit an endpoint every 5 mins, and if it's not hit then
  you know the cron system is down)

- do perf tests with large numbers of re-ocurring tasks.  Is performance OK just iterating the whole list every minute?
