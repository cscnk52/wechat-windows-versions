import httpx, re, subprocess, hashlib
from dateutil import parser, tz
from pathlib import Path

state = {
    "version": "",
    "download_link": "",
    "SHA256": "",
    "last_modified": "",
}


def extract_official_time():
    website = httpx.get("https://pc.weixin.qq.com/")
    download_link_re = re.search(
        r"https://dldir1v6\.qq\.com/weixin/Universal/Windows/WeChatWin_([\d\.]+)\.exe",
        website.text,
    )
    assert download_link_re, "download link not find"
    download_link_text = download_link_re.group(0)
    state["download_link"] = download_link_text
    download = httpx.head(download_link_text)
    time_text = download.headers.get("Last-Modified")
    return parser.parse(time_text)


def extract_repo_time():
    github_api_response = httpx.get(
        "https://api.github.com/repos/cscnk52/wechat-windows-versions/releases/latest"
    ).json()
    time_text_re = re.search(r"Last Modified:\s*(.+)", github_api_response["body"])
    assert time_text_re, "repo time_date match failed"
    time_date = parser.parse(time_text_re.group(1))
    time_date = time_date.replace(tzinfo=tz.tzutc())
    return time_date


def extract_installer_version():
    build_dir = Path("build")
    build_dir.mkdir(exist_ok=True)

    download_link = state["download_link"]
    assert download_link, "Download link is not initialized"
    response = httpx.get(download_link)
    response.raise_for_status()

    install_path = build_dir / "weixin.exe"

    with open(install_path, "wb") as f:
        f.write(response.content)

    extract_exe_dir = build_dir / "exe"

    subprocess.run(
        ["7z", "x", str(install_path), f"-o{extract_exe_dir}", "-y"],
        capture_output=True,
        text=True,
    )

    install_7z_path = extract_exe_dir / "install.7z"
    extract_install_7z_path = build_dir / "install"

    subprocess.run(
        ["7z", "x", str(install_7z_path), f"-o{extract_install_7z_path}", "-y"],
        capture_output=True,
        text=True,
    )

    version_pattern = re.compile(r"^\d+(\.\d+)+$")

    version = None

    for p in extract_install_7z_path.iterdir():
        if p.is_dir() and version_pattern.match(p.name):
            version = p.name
            break

    assert version, "not find version string"
    state["version"] = version


def sha256():
    file_path = Path("build/weixin.exe")
    data = file_path.read_bytes()
    state["SHA256"] = hashlib.sha256(data).hexdigest()


def main():
    official_time = extract_official_time()
    repo_time = extract_repo_time()
    # if official_time <= repo_time:
    #     print("version is up to date")
    #     return
    state["last_modified"] = str(max(official_time, repo_time))
    extract_installer_version()
    sha256()
    print(state)


if __name__ == "__main__":
    main()
