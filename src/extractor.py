import re
import tempfile
import subprocess
import logging
from pathlib import Path
from typing import Optional

from .config import BIN_FILE


def extract_version_from_install() -> Optional[str]:
    """Extract version number from decompressed files"""
    if not BIN_FILE.exists():
        logging.error(f"File not found: {BIN_FILE}")
        return None

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Extract main file
            logging.info("Extracting main file")
            result = subprocess.run(
                ["7z", "x", str(BIN_FILE), f"-o{temp_path}", "-y"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                logging.error("Failed to extract main file")
                return None

            # Find install.7z
            install_7z_path = None
            for file_path in temp_path.rglob("install.7z"):
                install_7z_path = file_path
                break

            if not install_7z_path:
                logging.error("install.7z file not found")
                return None

            # Extract install.7z
            logging.info("Extracting install.7z")
            install_temp_dir = temp_path / "install_extracted"
            install_temp_dir.mkdir()

            result = subprocess.run(
                ["7z", "x", str(install_7z_path), f"-o{install_temp_dir}", "-y"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode != 0:
                logging.error("Failed to extract install.7z")
                return None

            # Search for version number
            version_pattern = re.compile(r"\b\d+\.\d+\.\d+\.\d+\b")
            for folder_path in install_temp_dir.iterdir():
                if folder_path.is_dir():
                    matches = version_pattern.findall(folder_path.name)
                    if matches:
                        version = matches[0]
                        logging.info(f"Version found: {version}")
                        return version

            logging.warning("Version number not found")
            return None

    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        return None
