"""
Provides command-line entry to the package
"""

import asyncio

from pjobq import run


def main():
    asyncio.run(run())
    return


if __name__ == "__main__":
    main()
