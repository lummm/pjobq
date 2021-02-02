"""
Runtime state.
Note that runtime state is mutable.
Because we are single threaded this doesn't really present an issue,
so long as we aren't careless with mutability.
"""

import asyncio
from dataclasses import dataclass

from ..apptypes import CronJob, PgNotifyListener, NotifyChannel, JobHandler, AdhocJob
from ..models import CronJobModel, AdhocJobModel
from ..db import DB
from ..apphttp import AppHttp
from .adhoc_scheduler import AdhocScheduler
from .cron_scheduler import CronScheduler


@dataclass
class State:
    """
    db: database interface
    cron_model: interface to cron_job table
    adhoc_model: interface to adhoc_job table
    cron_jobs: all known cron_jobs
    adhoc_scheduler: adhoc job scheduling service
    """

    db: DB
    cron_model: CronJobModel
    adhoc_model: AdhocJobModel
    http: AppHttp
    loop: asyncio.AbstractEventLoop
    adhoc_scheduler: AdhocScheduler
    cron_scheduler: CronScheduler
