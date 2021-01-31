"""
Test state.
Since we're testing scheduling, most tests are wrapped
in a timeout somewhere, in case something is not scheduled.
"""

import asyncio
import os

import asyncpg


DEFAULT_REQ_TIMEOUT_S = 10

TEST_URL = "http://test:8888/"


def fail():
    raise Exception("tests failed")
    return


async def con_db():
    return await asyncpg.connect(
            user=os.environ["PGUSER"],
            password=os.environ["PGPASSWORD"],
            database=os.environ["PGDB"],
            host=os.environ["PGHOST"],
        )


class TestEnv:
    @staticmethod
    async def init(
            *,
            req_q: asyncio.Queue,
    ):
        this = TestEnv()
        this.req_q = req_q
        this.db = await con_db()
        return this

    async def wait_next_req(
            self,
            timeout: int = DEFAULT_REQ_TIMEOUT_S
    ) -> str:
        return await asyncio.wait_for(
            self.req_q.get(),
            timeout
        )

    def assert_eq(self, exp, act):
        if exp != act:
            print("expected: ", exp, "actual: ", act)
            fail()
        return

    async def create_cron_job(
            self,
            schedule: str,
            *,
            payload: str,
            name: str,
    ):
        """
        All test cron jobs are assumed to be http POSTs to the test server.
        """
        sql = """
        SELECT cron_job_create_http(
          p_cron_schedule => $1,
          p_job_name => $2,
          p_http_method => 'POST',
          p_url => $3,
          p_body => $4
        )
        """
        return await self.execute(sql, [schedule, name, TEST_URL, payload])

    async def create_adhoc_job(
            self,
            ts: float,
            *,
            payload: str,
            name: str,
    ):
        """
        All test cron jobs are assumed to be http POSTs to the test server.
        """
        sql = """
        SELECT adhoc_job_create_http(
          p_schedule_ts => to_timestamp($1),
          p_job_name => $2,
          p_http_method => 'POST',
          p_url => $3,
          p_body => $4
        )
        """
        return await self.execute(sql, [schedule, name, TEST_URL, payload])

    async def cleanup(self):
        """
        Clean up the database.
        """
        sql = """
        TRUNCATE TABLE cron_job;
        TRUNCATE TABLE adhoc_job;
        """
        return await self.execute(sql)

    async def execute(self, sql, bindargs = []):

        async with self.db.transaction():
            return await self.db.execute(sql, *bindargs)
        return

    async def fetch(self, sql, bindargs = []):
        async with self.db.transaction():
            return await self.db.fetch(sql, *bindargs)
        return
