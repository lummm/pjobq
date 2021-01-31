EXTENSION_UUID = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
"""


TABLE_CRON_JOB = """
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
"""


FN_CRON_JOB_CREATE = """
CREATE OR REPLACE FUNCTION cron_job_create(
  IN p_cron_schedule  cron_job.cron_schedule%TYPE,
  IN p_job_name  cron_job.job_name%TYPE,
  IN p_cmd_type  cron_job.cmd_type%TYPE,
  IN p_cmd_payload  cron_job.cmd_payload%TYPE,
  IN p_enabled  cron_job.enabled%TYPE DEFAULT TRUE
)
RETURNS UUID
AS $$
DECLARE
  v_job_id  UUID  := uuid_generate_v1mc();
BEGIN
  IF NOT (p_cmd_type = 'HTTP' OR
          p_cmd_type = 'EZ')
  THEN
    RAISE EXCEPTION 'invalid cmd_type -> %', p_cmd_type;
  END IF;
  INSERT INTO cron_job (
                job_id,
                job_name,
                cron_schedule,
                cmd_type,
                cmd_payload,
                enabled
              )
       VALUES (
                v_job_id,
                p_job_name,
                TRIM(p_cron_schedule),
                p_cmd_type,
                p_cmd_payload,
                p_enabled
              )
              ;
  PERFORM pg_notify('cron_job', 'update');
  RETURN v_job_id;
END;
$$
LANGUAGE plpgsql
;
"""


FN_CRON_JOB_CREATE_HTTP = """
CREATE OR REPLACE FUNCTION cron_job_create_http(
  IN p_cron_schedule  cron_job.cron_schedule%TYPE,
  IN p_job_name  cron_job.job_name%TYPE,
  IN p_http_method  TEXT,
  IN p_url  TEXT,
  IN p_body  TEXT  DEFAULT '',
  IN p_enabled  cron_job.enabled%TYPE DEFAULT TRUE
)
RETURNS UUID
AS $$
BEGIN
  RETURN cron_job_create(
    p_cron_schedule => p_cron_schedule,
    p_job_name => p_job_name,
    p_enabled => p_enabled,
    p_cmd_type => 'HTTP',
    p_cmd_payload => jsonb_build_object(
      'method', p_http_method,
      'url', p_url,
      'body', p_body
    )::TEXT
  );
END;
$$
LANGUAGE plpgsql
;
"""
