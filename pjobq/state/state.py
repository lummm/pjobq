"""
Runtime state.
Note that runtime state is mutable.
Because we are single threaded this doesn't really present an issue,
so long as we aren't careless with mutability.
"""

from dataclasses import dataclass

from pjobq.apphttp import AppHttp
from pjobq.apptypes import EventLoop
from pjobq.db import DB
from pjobq.models import CronJobModel, AdhocJobModel

from .adhoc_scheduler import AdhocSchedulerState
from .cron_scheduler import CronSchedulerState


@dataclass
class State:
    """
    contains the app state
    """

    db: DB
    cron_model: CronJobModel
    adhoc_model: AdhocJobModel
    http: AppHttp
    loop: EventLoop
    adhoc_scheduler: AdhocSchedulerState
    cron_scheduler: CronSchedulerState
