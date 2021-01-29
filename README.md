* JOBS
A DB - defined job queue ala cron.
- python process stays in sync with 'cron' table,
  and launches jobs per schedule.


* impl
- define db function to schedule a recurring daily job,
  with TZ and hours:mins


* next steps
- failure notifications

- do perf tests with large numbers of re-ocurring tasks.  Is performance OK just iterating the whole list every minute?
