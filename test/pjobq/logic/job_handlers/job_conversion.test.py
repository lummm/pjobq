import json
import unittest

from pjobq.apptypes import Job, CronJob, HttpJob
import pjobq.logic.job_handlers.job_conversion as job_conversion

from testutils.fixtures import job, cron_job, http_get_payload


class TestJobConversion(unittest.TestCase):

    def test_as_http_job(self):
        self.assertEqual(job_conversion.as_http_job(job()), HttpJob(
            job_id="an-id",
            job_name="a-name",
            cmd_type="HTTP",
            cmd_payload=http_get_payload(),
            method="GET",
            url="http://testing.com",
            body=None,
        ))
        return

    def test_base_job_dict(self):
        expected_dict = {
            "job_id": "an-id",
            "job_name": "a-name",
            "cmd_type": "HTTP",
            "cmd_payload": http_get_payload(),
        }
        self.assertEqual(job_conversion.base_job_dict(job()), expected_dict)
        self.assertEqual(job_conversion.base_job_dict(cron_job()), expected_dict)
        return


if __name__ == '__main__':
    unittest.main()
