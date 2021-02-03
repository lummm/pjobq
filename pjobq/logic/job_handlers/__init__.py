"""
This package defines handlers to fire when a job needs to be run.

Job handling should always be executing in the context of an asycnio task (thus we can await as we please and not block firing off other jobs).
Job handling should ideally be pure I/O, as we are single threaded.
"""

from .handlers import handle_http
