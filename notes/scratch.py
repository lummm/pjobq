import asyncio
import json
import time

import pjobq


adhoc, cron = None, None


async def init():
    global adhoc
    global cron
    adhoc, cron = await pjobq.get_models()
    return



async def make_job(offset):
    await adhoc.create_job(
        schedule_ts=time.time() + offset,
        job_name="test-job",
        cmd_type="HTTP",
        cmd_payload=json.dumps({"method": "GET", "url": "http://www.google.com"}))
    return


async def run_test(n):
    await asyncio.gather(*[
        make_job(1)
        for i in range(n)])
