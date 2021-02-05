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


async def make_cron_job(schedule, name):
    await cron.create_job(
        cron_schedule=schedule,
        job_name=name,
        cmd_type="HTTP",
        cmd_payload=json.dumps({"method": "GET", "url": "http://www.google.com"}))
    return


async def make_adhoc_job(offset):
    await adhoc.create_job(
        schedule_ts=time.time() + offset,
        job_name="test-job",
        cmd_type="HTTP",
        cmd_payload=json.dumps({"method": "GET", "url": "http://www.google.com"}))
    return


async def run_test(n):
    await asyncio.gather(*[
        make_adhoc_job(1)
        for i in range(n)])


async def main():
    import time
    t0 = time.time()
    t1 = None
    def cb():
        nonlocal t1
        t1 = time.time()
        return
    loop = asyncio.get_event_loop()
    loop.call_later(0.1, cb)
    await asyncio.sleep(1)
    print(t1 - t0)
    return


if __name__ == '__main__':
    asyncio.run(main())
