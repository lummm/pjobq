EXTENSION_UUID = """
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
"""


FN_CHECK_CMD_TYPE = """
CREATE OR REPLACE FUNCTION check_cmd_type(
  IN p_cmd_type  TEXT
)
RETURNS BOOLEAN
AS $$
BEGIN
  IF NOT (p_cmd_type = 'HTTP' OR
          p_cmd_type = 'ZMQ' OR
          p_cmd_type = 'SQL')
  THEN
    RAISE EXCEPTION 'invalid cmd_type -> %', p_cmd_type;
  END IF;
  RETURN TRUE;
END;
$$
LANGUAGE plpgsql
IMMUTABLE
;

"""


TABLE_CRON_JOB = """
CREATE TABLE IF NOT EXISTS cron_job (
  job_id  UUID   NOT NULL  DEFAULT uuid_generate_v1mc(),
  created  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  enabled  BOOLEAN  NOT NULL  DEFAULT TRUE,
  timezone  TEXT  NOT NULL,
  job_name  TEXT  NOT NULL,
  cron_schedule  TEXT  NOT NULL,
  cmd_type  TEXT  NOT NULL
    CHECK (check_cmd_type(cmd_type)),
  cmd_payload  TEXT  NOT NULL,

  PRIMARY KEY (job_id),
  UNIQUE (job_name)
);

COMMENT ON TABLE cron_job IS 'Jobs scheduled with cron syntax';
COMMENT ON COLUMN cron_job.job_id IS 'Unique job ID.';
COMMENT ON COLUMN cron_job.created IS 'Time job created';
COMMENT ON COLUMN cron_job.enabled IS 'Whether cron job is enabled';
COMMENT ON COLUMN cron_job.timezone IS 'Timezone in which cron expression should be evaluated.  Ex. America/Vancouver.';
COMMENT ON COLUMN cron_job.job_name IS 'Human readable name for job';
COMMENT ON COLUMN cron_job.cron_schedule IS 'Cron syntax schedule for job';
COMMENT ON COLUMN cron_job.cmd_type IS 'Type of command.  See "check_cmd_type".';
COMMENT ON COLUMN cron_job.cmd_payload IS 'Arguments for command.';
"""


FN_CRON_JOB_CREATE = """
CREATE OR REPLACE FUNCTION cron_job_create(
  IN p_cron_schedule  cron_job.cron_schedule%TYPE,
  IN p_job_name  cron_job.job_name%TYPE,
  IN p_cmd_type  cron_job.cmd_type%TYPE,
  IN p_cmd_payload  cron_job.cmd_payload%TYPE,
  IN p_timezone  cron_job.timezone%TYPE  DEFAULT 'UTC',
  IN p_enabled  cron_job.enabled%TYPE  DEFAULT TRUE
)
RETURNS UUID
AS $$
DECLARE
  v_job_id  UUID  := uuid_generate_v1mc();
BEGIN
  INSERT INTO cron_job (
                job_id,
                job_name,
                cron_schedule,
                cmd_type,
                cmd_payload,
                timezone,
                enabled
              )
       VALUES (
                v_job_id,
                p_job_name,
                TRIM(p_cron_schedule),
                p_cmd_type,
                p_cmd_payload,
                p_timezone,
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
  IN p_timezone  cron_job.timezone%TYPE  DEFAULT 'UTC',
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
    )::TEXT,
    p_timezone  => p_timezone
  );
END;
$$
LANGUAGE plpgsql
;
"""

TABLE_ADHOC_JOB = """
CREATE TABLE IF NOT EXISTS adhoc_job (
  job_id  UUID   NOT NULL  DEFAULT uuid_generate_v1mc(),
  created  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  job_name  TEXT  NOT NULL,
  schedule_ts  TIMESTAMPTZ  NOT NULL,
  completed_ts  TIMESTAMPTZ,
  cmd_type  TEXT  NOT NULL
    CHECK (check_cmd_type(cmd_type)),
  cmd_payload  TEXT  NOT NULL,

  PRIMARY KEY (job_id)
);

COMMENT ON TABLE adhoc_job IS 'Adhoc jobs specified at a specific time.';
COMMENT ON COLUMN adhoc_job.job_id IS 'Unique job ID.';
COMMENT ON COLUMN adhoc_job.created IS 'Time job created';
COMMENT ON COLUMN adhoc_job.job_name IS 'Human readable name for job';
COMMENT ON COLUMN adhoc_job.schedule_ts IS 'Time at which to run job.';
COMMENT ON COLUMN adhoc_job.completed_ts IS 'If not null, time at which job completed.  O/w job is incomplete.';
COMMENT ON COLUMN adhoc_job.cmd_type IS 'Type of command.  See "check_cmd_type".';
COMMENT ON COLUMN adhoc_job.cmd_payload IS 'Arguments for command.';
"""


FN_ADHOC_JOB_CREATE = """
CREATE OR REPLACE FUNCTION adhoc_job_create(
  IN p_schedule_ts  adhoc_job.schedule_ts%TYPE,
  IN p_job_name  adhoc_job.job_name%TYPE,
  IN p_cmd_type  adhoc_job.cmd_type%TYPE,
  IN p_cmd_payload  adhoc_job.cmd_payload%TYPE
)
RETURNS UUID
AS $$
DECLARE
  v_job_id  UUID  := uuid_generate_v1mc();
BEGIN
  INSERT INTO adhoc_job (
                job_id,
                job_name,
                cmd_type,
                cmd_payload,
                schedule_ts
              )
       VALUES (
                v_job_id,
                p_job_name,
                p_cmd_type,
                p_cmd_payload,
                p_schedule_ts
              )
              ;
  PERFORM pg_notify('adhoc_job', 'update');
  RETURN v_job_id;
END;
$$
LANGUAGE plpgsql
;

"""


FN_ADHOC_JOB_CREATE_HTTP = """
CREATE OR REPLACE FUNCTION adhoc_job_create_http(
  IN p_schedule_ts  adhoc_job.schedule_ts%TYPE,
  IN p_job_name  adhoc_job.job_name%TYPE,
  IN p_http_method  TEXT,
  IN p_url  TEXT,
  IN p_body  TEXT  DEFAULT ''
)
RETURNS UUID
AS $$
BEGIN
  RETURN adhoc_job_create(
    p_schedule_ts => p_schedule_ts,
    p_job_name => p_job_name,
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


FN_CRON_JOB_DELETE = """
CREATE OR REPLACE FUNCTION cron_job_delete(
  IN p_job_names  TEXT[]
)
RETURNS INTEGER
AS $$
DECLARE
  v_job_count  INTEGER;
BEGIN
  WITH deleted AS (
    DELETE FROM cron_job
          WHERE job_name = ANY(p_job_names)
      RETURNING *
  ) SELECT count(*)
      INTO v_job_count
      FROM deleted
  ;
  PERFORM pg_notify('cron_job', 'update');
  RETURN v_job_count;
END;
$$
LANGUAGE plpgsql
;
"""


FN_ADHOC_JOB_DELETE = """
CREATE OR REPLACE FUNCTION adhoc_job_delete(
  IN p_job_names  TEXT[]
)
RETURNS INTEGER
AS $$
DECLARE
  v_job_count  INTEGER;
BEGIN
  WITH deleted AS (
    DELETE FROM adhoc_job
          WHERE job_name = ANY(p_job_names)
      RETURNING *
  ) SELECT count(*)
      INTO v_job_count
      FROM deleted
  ;
  PERFORM pg_notify('adhoc_job', 'update');
  RETURN v_job_count;
END;
$$
LANGUAGE plpgsql
;
"""
