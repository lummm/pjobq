from .test_env import TestEnv
from . import simple_cron_test
from . import adhoc_job_test

TESTS = [
    *simple_cron_test.TESTS,
    *adhoc_job_test.TESTS,
]
