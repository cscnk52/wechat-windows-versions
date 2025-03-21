#!/bin/bash

# 全局变量
URL="https://dldir1v6.qq.com/weixin/Universal/Windows/WeChatWin.exe"
VERSION_FILE="version.txt"
HASH_FILE="hash.txt"
LAST_MODIFY_FILE="last_modified.txt"
URL_FILE="url.txt"

# 安装依赖
install_dependencies() {
    sudo apt update
    sudo apt install -y curl p7zip-full jq
}

# 获取 GitHub 上最新 Release 的 last-modify 时间
get_latest_github_release_last_modify() {
    local api_url="https://api.github.com/repos/${GITHUB_REPOSITORY}/releases/latest"
    local last_modify=$(curl -s "$api_url" | jq -r '.body' | grep -i "Last Modified" | sed 's/[*]*Last Modified:[*]* //i')
    if [ -z "$last_modify" ]; then
        last_modify="未找到"
    fi
    echo "$last_modify"
}

# 检查是否需要下载文件
check_and_download() {
    latest_github_last_modify=$(get_latest_github_release_last_modify)
    current_last_modify=$(curl -sI "$URL" | grep -i "Last-Modified" | awk '{print $2, $3, $4, $5, $6}')
    if [ -z "$current_last_modify" ]; then
        echo "未获取到当前文件的 Last-Modified 时间。"
        exit 1
    fi
    current_timestamp=$(date -d "$current_last_modify" +%s)
    if [ "$latest_github_last_modify" != "未找到" ]; then
        latest_github_timestamp=$(date -d "$latest_github_last_modify" +%s)
        if [ "$current_timestamp" -le "$latest_github_timestamp" ]; then
            echo "文件没有更新。"
            exit 0
        fi
    fi
    echo "发现更新的文件！开始下载..."
    curl -o "WeChatWin.exe" "$URL"
    echo "$current_last_modify" > "$LAST_MODIFY_FILE"
    echo "$URL" > "$URL_FILE"
}

# 计算文件的 SHA-256 哈希值
calculate_sha256() {
    sha256_hash=$(sha256sum WeChatWin.exe | awk '{print $1}')
    echo "WeChatWin.exe 的 SHA-256 哈希值为: $sha256_hash"
    echo "$sha256_hash" > "$HASH_FILE"
    echo "$sha256_hash"
}

# 解压文件并匹配版本号
extract_and_match_version() {
    7z x "WeChatWin.exe" -y
    if [ -f "install.7z" ]; then
        echo "查看 install.7z 内容..."
        version_folder=$(7z l "install.7z" | grep -Eo '[0-9]+\.[0-9]+\.[0-9]+(\.[0-9]+)?' | head -n 1)
        if [ -n "$version_folder" ]; then
            version=$version_folder
            echo "匹配到的版本号是: $version"
        else
            echo "未匹配到版本号文件夹。"
            version="未找到"
        fi
    else
        echo "未找到 install.7z 文件。"
        version="未找到"
    fi
    echo "$version" > "$VERSION_FILE"
    echo "$version"
}

# 主函数
main() {
    install_dependencies
    check_and_download
    sha256_hash=$(calculate_sha256)
    version=$(extract_and_match_version)
    echo "信息已保存到以下文件："
    echo "URL: $URL_FILE"
    echo "版本号: $VERSION_FILE"
    echo "哈希值: $HASH_FILE"
    echo "Last-Modified: $LAST_MODIFY_FILE"
}

# 执行主函数
main
