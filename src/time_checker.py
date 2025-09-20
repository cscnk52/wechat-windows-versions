import aiohttp
from typing import Any, Optional, Tuple
from dateutil.parser import parse
from datetime import datetime, timezone
import logging

from .config import DOWNLOAD_URL, GITHUB_LATEST_RELEASE_API


async def get_official_modify_time() -> Optional[datetime]:
    """Get official modify time from download URL"""
    async with aiohttp.ClientSession() as session:
        async with session.head(DOWNLOAD_URL) as response:
            last_modified_str = response.headers.get("Last-Modified")
            if last_modified_str:
                last_modified = parse(last_modified_str)
                logging.info(f"Official modify time: {last_modified}")
                return last_modified
            else:
                return None


async def get_repo_modify_time() -> Optional[datetime]:
    """Get repository modify time from GitHub API"""
    async with aiohttp.ClientSession() as session:
        async with session.get(GITHUB_LATEST_RELEASE_API) as response:
            data: dict[str, Any] = await response.json()
            body: str = data["body"]
            time_str = body.split("**Last Modified:**", 1)[1].strip()
            if time_str:
                time = parse(time_str)
                if time.tzinfo is None:
                    time = time.replace(tzinfo=timezone.utc)
                logging.info(f"Repo modify time: {time}")
                return time
            else:
                return None


async def check_for_updates() -> Tuple[bool, Optional[datetime], Optional[datetime]]:
    """Check if there are updates available"""
    official_time = await get_official_modify_time()
    repo_time = await get_repo_modify_time()

    has_update = False
    if official_time and (repo_time is None or official_time > repo_time):
        has_update = True
        logging.info("Update detected!")
    else:
        logging.info("No update needed")

    return has_update, official_time, repo_time
