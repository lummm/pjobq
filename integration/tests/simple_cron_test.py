async def every_minute_test(t):
    await t.create_cron_job("* * * * *", "test-job", "payload1")
    req = await t.wait_next_req(62) # should occur within a min
    t.assert_eq(req, "payload1")
    return


TESTS = [every_minute_test]
