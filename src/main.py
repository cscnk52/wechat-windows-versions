import asyncio
from os import environ
import aiohttp
from typing import Any, Final, Optional
from dateutil.parser import parse
from datetime import datetime, timezone
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

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
            last_modified_str = response.headers.get("Last-Modified")
            if last_modified_str:
                last_modified = parse(last_modified_str)
                logging.info(f"Official modify time: {last_modified}")
                return last_modified
            else:
                return None


async def get_repo_modify_time() -> Optional[datetime]:
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



def set_github_ci_output(key: str, value: str):
    if "GITHUB_OUTPUT" in environ:
        with open(environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"{key}={value}\n")
            logging.debug(f"GITHUB_OUTPUT << {key}={value}")


async def main():
    await get_official_modify_time()
    await get_repo_modify_time()


if __name__ == "__main__":
    asyncio.run(main())
