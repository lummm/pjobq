"""
Logic related to scheduling adhoc jobs.
We mark a job as completed upon successfully performing it.
"""
from datetime import datetime
import logging
import time

from pjobq.apptypes import JobHandler, Job, AdhocJob, EventLoop, PgNotifyListener
from pjobq.constants import ADHOC_JOB_INTERVAL_S, NOTIFY_UPDATE_CMD
from pjobq.models import AdhocJobModel
from pjobq.state import AdhocSchedulerState
from pjobq.util import delay_execution, create_unfailing_task


async def run_adhoc_job(
    adhoc_job_model: AdhocJobModel,
    handler: JobHandler,
    job: Job,
) -> None:
    """
    Attempt to run 'handler'.
    On success, update DB record for job.
    """
    await handler(job)
    await adhoc_job_model.set_job_completed(job.job_id)
    return


def schedule_adhoc_jobs(
    scheduler: AdhocSchedulerState,
    loop: EventLoop,
    jobs: list[AdhocJob],
    handler: JobHandler,
) -> None:
    "purely additive for the moment - ie. we don't 'unschedule' any jobs"
    for job in jobs:
        if job.job_id in scheduler.scheduled:
            scheduler.scheduled[job.job_id].cancel()
        job_exec_awaitable = run_adhoc_job(scheduler.adhoc_job_model, handler, job)
        scheduler.scheduled[job.job_id] = create_unfailing_task(
            job.job_id, loop, delay_execution(job_exec_awaitable, job.schedule_ts)
        )
    return


async def update_adhoc_window(
    loop: EventLoop,
    handler: JobHandler,
    scheduler: AdhocSchedulerState,
) -> None:
    "bumpthe window forward ADHOC_JOB_INTERVAL_S seconds, then load any jobs in the window"
    scheduler.start_time = time.time()
    scheduler.end_time = scheduler.start_time + ADHOC_JOB_INTERVAL_S
    await reload_jobs_in_adhoc_window(loop, handler, scheduler)
    return


def on_adhoc_table_notify_factory(
    loop: EventLoop,
    scheduler: AdhocSchedulerState,
    handler: JobHandler,
) -> PgNotifyListener:
    """
    Generate a handler for pg_notify events for the adhoc_job table.
    """

    def on_adhoc_table_notify(payload: str) -> None:
        if payload == NOTIFY_UPDATE_CMD:
            create_unfailing_task(
                "adhoc job table refresh",
                loop,
                reload_jobs_in_adhoc_window(loop, handler, scheduler),
            )
            return
        logging.error("unknown cron notify payload -> %s", payload)
        return

    return on_adhoc_table_notify


# private
async def reload_jobs_in_adhoc_window(
    loop: EventLoop,
    handler: JobHandler,
    scheduler: AdhocSchedulerState,
) -> None:
    """Load all jobs in the window"""
    jobs = await scheduler.adhoc_job_model.get_all_in_range(
        scheduler.start_time, scheduler.end_time
    )
    logging.debug(
        "loaded %s adhoc jobs in window %s - %s",
        len(jobs),
        datetime.fromtimestamp(scheduler.start_time).isoformat(),
        datetime.fromtimestamp(scheduler.end_time).isoformat(),
    )
    schedule_adhoc_jobs(scheduler, loop, jobs, handler)
    return
