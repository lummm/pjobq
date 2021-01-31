#!/usr/bin/env python3.9

"""
This is the entry point to run integration tests from.
This should execute inside the system defined by the docker-compose file.

We spin up a test http server which our jobs will make requests to.
"""

import asyncio
import os
from pprint import pformat

from aiohttp import web

import tests


TEST_SERVER_PORT = int(os.environ.get("TEST_SERVER_PORT", "8888"))


async def debug_failure(test_env):
    cron_jobs = await test_env.fetch("""
    SELECT * FROM cron_job;
    """)
    adhoc_jobs = await test_env.fetch("""
    SELECT * FROM adhoc_job;
    """)
    print("cron jobs:\n", pformat(cron_jobs))
    print("adhoc jobs:\n", pformat(adhoc_jobs))
    return


async def start_test_http_server(req_q: asyncio.Queue):
    """
    Run a test http server.
    All requests are just passed back into a queue to be handled elsewhere.
    """
    async def base_handler(req):
        body = await req.text()
        req_q.put_nowait(body)
        return web.Response(text="TEST-OK")
    app = web.Application()
    app.add_routes([web.post("/", base_handler)])
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', TEST_SERVER_PORT)
    await site.start()
    return


async def run_tests(req_q: asyncio.Queue):
    test_env = await tests.TestEnv.init(req_q = req_q)
    try:
        for test in tests.TESTS:
            await test_env.cleanup()
            await test(test_env)
    except Exception as e:
        await debug_failure(test_env)
        # must bring down whole loop
        loop = asyncio.get_event_loop()
        loop.stop()
        raise(e)
    return


async def main():
    req_q = asyncio.Queue()
    await asyncio.gather(*[
        start_test_http_server(req_q),
        run_tests(req_q),
    ])
    return


if __name__ == '__main__':
    asyncio.run(main())
