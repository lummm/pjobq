import time


async def adhoc_job_test1(t):
    schedule_ts = time.time() + 4
    print("creating....")
    await t.create_adhoc_job(schedule_ts, "test-job", "adhoc-payload-1")
    req = await t.wait_next_req(5)
    print("received", req)
    t.assert_eq(req, "adhoc-payload-1")
    return


TESTS = [adhoc_job_test1]
