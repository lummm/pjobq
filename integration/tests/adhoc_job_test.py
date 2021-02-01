import time


async def adhoc_job_test1(t):
    schedule_ts = time.time() + 2
    await t.create_adhoc_job(schedule_ts, name="test-job", payload="adhoc-payload-1")
    req = await t.wait_next_req(3)
    t.assert_eq(req, "adhoc-payload-1")
    return


TESTS = [adhoc_job_test1]
