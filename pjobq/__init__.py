"""
We expose:
- the application runner
- an interface into the models (mostly for running at the repl)
"""

from .bootstrap import run_application


async def get_models():
    from .db import DBImpl
    from .models import AdhocJobModelImpl, CronJobModelImpl

    db = DBImpl()
    await db.init()
    adhoc_model = AdhocJobModelImpl()
    cron_model = CronJobModelImpl()
    await adhoc_model.init(db)
    await cron_model.init(db)
    return (adhoc_model, cron_model)
