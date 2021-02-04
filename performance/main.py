#!/usr/bin/env python3

import asyncio
import json
import os
import pprint
import time
from uuid import uuid4
os.environ["PGPASSWORD"] = "performance-testing"

from aiohttp import web

from pjobq import get_models


class TestResults:
    def __init__(self):
        self.res = {}

    def set_received(self, res_id: str):
        self.res[res_id]["received"].append(time.time())
        return

    def set_sent(self, req_id: str, sched_time: float):
        self.res[req_id] = {
            "requested": sched_time,
            "received": [],
        }
        return


async def start_test_http_server(test: TestResults):
    async def base_handler(req):
        body = await req.text()
        test.set_received(body)
        # req_q.put_nowait(body)
        return web.Response(text="TEST-OK")
    app = web.Application()
    app.add_routes([web.post("/", base_handler)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 9999)
    print("starting test server...")
    await site.start()
    return


async def make_adhoc_job(create_job, at: float, req_id: str):
    await create_job(
        schedule_ts=at,
        job_name="test-job",
        cmd_type="HTTP",
        cmd_payload=json.dumps({"method": "POST", "url": "http://localhost:9999", "body": req_id}))
    return


async def test_many(n_tests: int, offset: float):
    loop = asyncio.get_event_loop()
    # req_q = asyncio.Queue()
    test = TestResults()
    adhoc, cron = await get_models()
    server_task = loop.create_task(start_test_http_server(test))
    await asyncio.sleep(2)
    print("starting tests")
    for i in range(n_tests):
        req_id  = str(uuid4())
        sched_time = time.time() + offset
        test.set_sent(req_id, sched_time)
        # print("req", req_id)
        await make_adhoc_job(adhoc.create_job, sched_time, req_id)
        # print("res", res)
    print("tests complete")
    await asyncio.sleep(5)      # let the server cool down
    for trial, result in test.res.items():
        if len(result["received"]) != 1:
            print(trial, pprint.pformat(result))
    return


async def main():
    import sys
    n_tests = int(sys.argv[1])
    offset = float(sys.argv[2])
    await test_many(n_tests, offset)
    return


if __name__ == '__main__':
    asyncio.run(main())
