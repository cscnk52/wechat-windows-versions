import asyncio
import logging

from .utils import setup_logging, set_github_ci_output
from .time_checker import check_for_updates


async def main():
    """Check for updates only"""
    setup_logging()

    # Check for updates
    has_update, official_time, repo_time = await check_for_updates() # type: ignore

    if has_update:
        logging.info("Update detected!")
        set_github_ci_output("has_update", "true")
        if official_time:
            set_github_ci_output("modified_time", official_time.isoformat())
    else:
        logging.info("No update needed")
        set_github_ci_output("has_update", "false")


if __name__ == "__main__":
    asyncio.run(main())
