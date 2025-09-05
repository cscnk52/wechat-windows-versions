import asyncio
import aiohttp
from typing import Any, Final, Optional
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

DOWNLOAD_URL: Final[str] = (
    "https://dldir1v6.qq.com/weixin/Universal/Windows/WeChatWin.exe"
)
REPO_HANDLE: Final[str] = "cscnk52/wechat-windows-versions"
GITHUB_LATEST_RELEASE_API: Final[str] = (
    f"https://api.github.com/repos/{REPO_HANDLE}/releases/latest"
)


async def get_official_modify_time() -> Optional[datetime]:
    async with aiohttp.ClientSession() as session:
        async with session.head(DOWNLOAD_URL) as response:
            last_modified = response.headers.get("Last-Modified")
            if last_modified:
                return parsedate_to_datetime(last_modified)
            else:
                return None


async def get_repo_modify_time() -> Optional[datetime]:
    async with aiohttp.ClientSession() as session:
        async with session.get(GITHUB_LATEST_RELEASE_API) as response:
            data: dict[str, Any] = await response.json()
            body: str = data["body"]
            time_str = body.split("**Last Modified:**", 1)[1].strip()
            if time_str:
                dt =  parsedate_to_datetime(time_str)
                return dt.replace(tzinfo=timezone.utc)
            else:
                return None


async def main():
    print(await get_official_modify_time())
    print(await get_repo_modify_time())


if __name__ == "__main__":
    asyncio.run(main())
