#!/usr/bin/env python3.9

"""
This is the entry point to run integration tests from.
This should execute inside the system defined by the docker-compose file.

We spin up a test http server which our jobs will make requests to.

All tests get a 'TestEnv' argument for things like db access, or reading the last request to the test server.
"""

import asyncio
import os
from pprint import pformat

from aiohttp import web

import tests


TEST_SERVER_PORT = int(os.environ.get("TEST_SERVER_PORT", "8888"))


async def debug_failure(test_env, error):
    print("TESTS FAILED - ", error)
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
    site = web.TCPSite(runner, '0.0.0.0', TEST_SERVER_PORT)
    print("starting test server...")
    await site.start()
    return


async def run_test(test_env, test):
    """
    Clean up the database before every test run.
    """
    print("running", test)
    await test_env.cleanup()
    await test(test_env)
    print("SUCCESS!", test)
    return


async def run_tests(req_q: asyncio.Queue):
    test_env = await tests.TestEnv.init(req_q = req_q)
    cmd_line_test_fn = os.environ.get("TEST_FN", None)
    try:
        if cmd_line_test_fn:    # only run the one test
            print("running single test fn", cmd_line_test_fn)
            fn = [test for test in tests.TESTS
                  if test.__name__ == cmd_line_test_fn][0]
            await run_test(test_env, fn)
            return
        for test in tests.TESTS: # o/w run all the tests
            await run_test(test_env, test)
    except Exception as e:
        await debug_failure(test_env, e)
        # must bring down whole loop
        loop = asyncio.get_event_loop()
        try:
            loop.stop()
        except:
            pass
        raise(e)
    return


async def main():
    loop = asyncio.get_event_loop()
    req_q = asyncio.Queue()
    for task in [
            loop.create_task(start_test_http_server(req_q)),
            loop.create_task(run_tests(req_q)),
    ]:
        await task
    return


if __name__ == '__main__':
    asyncio.run(main())
