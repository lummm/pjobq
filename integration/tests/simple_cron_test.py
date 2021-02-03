from datetime import datetime
from datetime import timedelta


async def recurring_time_test(t):
    """
    Set up a cron job for the next minute.
    """
    target = datetime.now().replace(second=0, microsecond=0) \
        + timedelta(minutes=1, seconds=30)
    print("scheduling a daily job for ", target.isoformat())
    cron_sched = f"{target.minute} {target.hour} * * *"
    await t.create_cron_job(cron_sched, name="recurring-test-job", payload="recurring-payload")
    req = await t.wait_next_req(92)
    t.assert_eq(req, "recurring-payload")
    return


async def every_minute_test(t):
    await t.create_cron_job("* * * * *", name="test-job", payload="payload1")
    req = await t.wait_next_req(62) # should occur within a min
    t.assert_eq(req, "payload1")
    req2 = await t.wait_next_req(62)
    t.assert_eq(req2, "payload1")
    return




TESTS = [
    recurring_time_test,
    every_minute_test,
]
