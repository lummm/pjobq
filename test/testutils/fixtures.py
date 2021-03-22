import json
import time

from pjobq.apptypes import Job, CronJob, HttpJob, AdhocJob


http_get_payload = lambda: json.dumps({
    "method": "GET",
    "url": "http://testing.com",
})
job = lambda: Job(
    job_id="an-id",
    job_name="a-name",
    cmd_type="HTTP",
    cmd_payload=http_get_payload(),
)
cron_job = lambda: CronJob(
    job_id="an-id",
    job_name="a-name",
    cmd_type="HTTP",
    cmd_payload=http_get_payload(),
    cron_schedule="* * * * *",
    timezone="UTC"
)
def adhoc_job(
        job_id = "an-id",
        schedule_ts = time.time()
):
    return AdhocJob(
        job_id=job_id,
        job_name="a-name",
        cmd_type="HTTP",
        cmd_payload=http_get_payload(),
        schedule_ts=schedule_ts,
    )
http_job = lambda: HttpJob(
    job_id="an-id",
    job_name="a-name",
    cmd_type="HTTP",
    cmd_payload=http_get_payload(),
    method="GET",
    url="http://testing.com",
)
