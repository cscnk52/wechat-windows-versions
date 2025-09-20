from pathlib import Path
from typing import Final
from urllib.parse import urlparse

DOWNLOAD_URL: Final[str] = (
    "https://dldir1v6.qq.com/weixin/Universal/Windows/WeChatWin.exe"
)
REPO_HANDLE: Final[str] = "cscnk52/wechat-windows-versions"
GITHUB_LATEST_RELEASE_API: Final[str] = (
    f"https://api.github.com/repos/{REPO_HANDLE}/releases/latest"
)

BUILD_DIR: Final[Path] = Path("build")
FILENAME = Path(urlparse(DOWNLOAD_URL).path).name
BIN_FILE = BUILD_DIR.joinpath(FILENAME)
