# Job Definitions

## HTTP
`cmd_type` is 'HTTP'

`cmd_payload` is expected to be a JSON-formatted payload containing the keys "method" and "url", and optionally "body".

- `method` must be a valid HTTP method
- `url` should include the connection protocol (ie. http://testing.com)
- `body`, if present, will be added as a body to the request
