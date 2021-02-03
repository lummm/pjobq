# pjobq architecture notes
At a high level, we are maintaining two tasks on the event loop, one of which handles cron-syntax style jobs, and the other handles arbitrary timestamp 'adhoc' jobs.

We listen for changes through pg_notify to either of these tables,
so we can always maintain state with the database.

## Code

As much as possible, we try to seperate state from logic.
In general dataclasses are preferred, with functions operating over them, instead of defining member funtions of a class.

### Points of interest
The following are important sections of the code:

[init_state](../pjobq/state/init_state.py)
This is where we specify the implementations of abstract classes, and populate a 'State' object with them.

[bootstrap](../pjobq/bootstrap.py)
This defines what the runtime looks like.
We run two major loops here 'run_cron_job_loop' and 'run_adhoc_job_loop'.
