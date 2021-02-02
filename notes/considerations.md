# Development concerns moving forward

## Performance
The single db connection can be easily overwhelmed by rapidly creating adhoc_jobs.

TODO:
Load a pool in the DB, then give each of the table listeners a dedicated connection.


## Testing
More performance tests need to be done in order to profile the system.

TODO:
Define a test that schedules adhoc jobs at a given time in the future and
waits for the response, then repeats this after a wait period, using incrementing response payloads.
Find the smallest wait interval that gives consistent responses.
