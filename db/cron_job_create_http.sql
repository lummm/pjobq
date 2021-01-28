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
