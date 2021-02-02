"""
Shared constants
"""

# topics called by pg_notify
CRON_NOTIFY_CHANNEL = "cron_job"
ADHOC_NOTIFY_CHANNEL = "adhoc_job"

# paylaods called by pg_notify
NOTIFY_UPDATE_CMD = "update"

# this controls the adhoc job rolling window size in seconds
ADHOC_JOB_INTERVAL_S = 60
