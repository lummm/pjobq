CREATE TABLE IF NOT EXISTS cron_job (
  job_id  UUID   NOT NULL  DEFAULT uuid_generate_v1mc(),
  created  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  updated  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  enabled BOOLEAN  NOT NULL  DEFAULT TRUE,
  job_name  TEXT  NOT NULL,
  cron_schedule  TEXT  NOT NULL,
  cmd_type  TEXT  NOT NULL,
  cmd_payload  TEXT  NOT NULL,

  PRIMARY KEY (job_id),
  UNIQUE (job_name)
);

COMMENT ON TABLE cron_job IS 'Jobs scheduled with cron syntax';
COMMENT ON COLUMN cron_job.job_id IS 'Unique job ID.';
COMMENT ON COLUMN cron_job.created IS 'Time job created';
COMMENT ON COLUMN cron_job.updated IS 'Time job last updated';
COMMENT ON COLUMN cron_job.enabled IS 'Whether cron job is enabled';
COMMENT ON COLUMN cron_job.job_name IS 'Human readable name for job';
COMMENT ON COLUMN cron_job.cron_schedule IS 'Cron syntax schedule for job';
COMMENT ON COLUMN cron_job.cmd_type IS 'Type of command.  "HTTP" or "EZ"';
COMMENT ON COLUMN cron_job.cmd_payload IS 'Arguments for command.';
