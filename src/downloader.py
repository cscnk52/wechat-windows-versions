import aiohttp
import logging

from .config import DOWNLOAD_URL, BUILD_DIR, BIN_FILE


async def download_file():
    """Download file to build directory"""
    BUILD_DIR.mkdir(parents=True, exist_ok=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(DOWNLOAD_URL) as response:
            response.raise_for_status()

            file_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            last_logged_percent = 0

            with open(BIN_FILE, "wb") as fd:
                async for chunk in response.content.iter_chunked(1024 * 1024):
                    fd.write(chunk)
                    downloaded += len(chunk)

                    if file_size > 0:
                        progress = downloaded / file_size * 100
                        current_percent = int(progress // 10) * 10

                        if (
                            current_percent > last_logged_percent
                            and current_percent % 10 == 0
                        ):
                            downloaded_mb = downloaded / (1024 * 1024)
                            total_mb = file_size / (1024 * 1024)
                            logging.info(
                                f"Download Progress: {current_percent}% ({downloaded_mb:.1f}MB/{total_mb:.1f}MB)"
                            )
                            last_logged_percent = current_percent

    logging.info(f"Download finished: {BIN_FILE}")
