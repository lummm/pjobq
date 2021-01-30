#!/usr/bin/env python3.9
"""
Provides entry to pjobq
"""

import asyncio

from pjobq import run_application


def main():
    asyncio.run(run_application())
    return


if __name__ == "__main__":
    main()
