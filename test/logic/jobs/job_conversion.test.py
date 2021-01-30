import json
import unittest

from pjobq.apptypes import Job, CronJob, HttpJob
import pjobq.logic.jobs.job_conversion as job_conversion


class TestJobConversion(unittest.TestCase):

    def test_as_http_job(self):
        payload = json.dumps({
            "method": "GET",
            "url": "http://testing.com",
        })
        job = Job(
            job_id="an-id",
            job_name="a-name",
            cmd_type="HTTP",
            cmd_payload=payload,
        )
        self.assertEqual(job_conversion.as_http_job(job), HttpJob(
            job_id="an-id",
            job_name="a-name",
            cmd_type="HTTP",
            cmd_payload=payload,
            method="GET",
            url="http://testing.com",
            body=None,
        ))
        return

    def test_base_job_dict(self):
        job = Job(
            job_id="an-id",
            job_name="a-name",
            cmd_type="HTTP",
            cmd_payload="garbage",
        )
        expected_dict = {
            "job_id": "an-id",
            "job_name": "a-name",
            "cmd_type": "HTTP",
            "cmd_payload": "garbage",
        }
        cron_job = CronJob(
            job_id="an-id",
            job_name="a-name",
            cmd_type="HTTP",
            cmd_payload="garbage",
            cron_schedule="* * * * *",
        )
        self.assertEqual(job_conversion.base_job_dict(job), expected_dict)
        self.assertEqual(job_conversion.base_job_dict(cron_job), expected_dict)
        return


if __name__ == '__main__':
    unittest.main()
