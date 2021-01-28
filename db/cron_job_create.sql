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
