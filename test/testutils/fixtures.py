import json
from pjobq.apptypes import Job, CronJob, HttpJob


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
)

http_job = lambda: HttpJob(
    job_id="an-id",
    job_name="a-name",
    cmd_type="HTTP",
    cmd_payload=http_get_payload(),
    method="GET",
    url="http://testing.com",
)
