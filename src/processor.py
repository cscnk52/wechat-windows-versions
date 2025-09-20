import asyncio
import logging

from .utils import setup_logging, set_github_ci_output, calculate_file_sha256
from .time_checker import check_for_updates
from .downloader import download_file
from .extractor import extract_version_from_install
from .config import BIN_FILE, DOWNLOAD_URL


def generate_release_notes(version: str, sha256: str, modified_time: str) -> str:
    """Generate release notes in the specified format"""
    return f"""Version: {version}
Download URL: {DOWNLOAD_URL}
SHA256: {sha256}
Last Modified: {modified_time}"""


async def main():
    """Download and process WeChat"""
    setup_logging()

    # Check for updates first
    has_update, official_time, repo_time = await check_for_updates() # type: ignore

    if has_update:
        logging.info("Starting download and processing...")

        # Download file
        await download_file()

        # Extract version
        version = extract_version_from_install()

        if version:
            logging.info(f"Version extracted: {version}")

            # Calculate SHA256
            logging.info("Calculating SHA256...")
            file_sha256 = calculate_file_sha256(BIN_FILE)

            # Format modified time
            modified_time_str = ""
            if official_time:
                modified_time_str = official_time.strftime("%a, %d %b %Y %H:%M:%S")

            # Generate release notes
            release_notes = generate_release_notes(version, file_sha256, modified_time_str)

            # Set GitHub Actions outputs
            set_github_ci_output("version", version)
            set_github_ci_output("has_update", "true")
            set_github_ci_output("file_path", str(BIN_FILE))
            set_github_ci_output("release_body", release_notes)
            set_github_ci_output("file_sha256", file_sha256)
            set_github_ci_output("tag_name", f"v{version}")
            if official_time:
                set_github_ci_output("modified_time", official_time.isoformat())

            logging.info("Release notes generated:")
            logging.info(release_notes)
        else:
            logging.warning("Version extraction failed")
            set_github_ci_output("has_update", "false")
    else:
        logging.info("No update needed")
        set_github_ci_output("has_update", "false")


if __name__ == "__main__":
    asyncio.run(main())
