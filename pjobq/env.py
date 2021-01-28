"""
Environment variables
"""

import os
from typing import NamedTuple


class _ENV(NamedTuple):
    # required
    PGPASSWORD: str = os.environ["PGPASSWORD"]
    # optional
    PGHOST: str = os.environ.get("PGHOST", "localhost")
    PGUSER: str = os.environ.get("PGUSER", "postgres")
    PGDB: str = os.environ.get("PGDB", "postgres")


ENV = _ENV()
