# Development concerns moving forward

## Road map
- Pull apart bootstrap.py to be more testable
- Tag a version, and cut a dev branch


## Testing
The bootstap module is difficult to unit test.
TODO:
Extract as much of the logic as possible to pure functions you can test.


More performance tests need to be done in order to profile the system.

TODO:
Define a test that schedules adhoc jobs at a given time in the future and
waits for the response, then repeats this after a wait period, using incrementing response payloads.
Find the smallest wait interval that gives consistent responses.
