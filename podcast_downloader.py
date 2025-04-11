#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import feedparser
import requests
from tqdm import tqdm
import argparse
import re
import json
from urllib.parse import urlparse
import time
import hashlib
import subprocess


def sanitize_filename(filename):
    """Clean filename by removing illegal characters"""
    # Replace characters not allowed in Windows and Unix filenames
    return re.sub(r'[\\/*?:"<>|#%&{}()@]', "_", filename)


def download_file(url, output_path):
    """Download file with progress bar"""
    try:
        # 添加超时设置和请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()  # Ensure request was successful

        # Get file size (if provided by server)
        total_size = int(response.headers.get("content-length", 0))

        # Create progress bar
        with (
            open(output_path, "wb") as f,
            tqdm(
                desc=os.path.basename(output_path),
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar,
        ):
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)
                    bar.update(len(chunk))
        return True
    except KeyboardInterrupt:
        print("\n下载被用户中断")
        # 删除部分下载的文件
        if os.path.exists(output_path):
            os.remove(output_path)
        raise  # 重新抛出KeyboardInterrupt异常以便主程序可以处理它
    except requests.exceptions.Timeout:
        print(f"\n下载超时: {url}")
        # 删除部分下载的文件
        if os.path.exists(output_path):
            os.remove(output_path)
        return False
    except Exception as e:
        print(f"\n下载失败: {e}")
        # Remove partially downloaded file if download fails
        if os.path.exists(output_path):
            os.remove(output_path)
        return False


def clean_html_text(html_content):
    """Remove HTML tags and clean up text content"""
    if not html_content:
        return ""
    # 使用正则表达式移除HTML标签
    text = re.sub(r"<[^>]+>", "", html_content)
    # 替换HTML实体
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    # 清理多余空白
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def save_description(entry, output_path):
    """Save podcast episode description and metadata to a JSON file"""
    try:
        # Extract relevant metadata
        metadata = {
            "title": entry.get("title", ""),
            "description": clean_html_text(entry.get("description", "")),
            "published": entry.get("published", ""),
            "link": entry.get("link", ""),
            "author": entry.get("author", ""),
            "tags": [tag.get("term", "") for tag in entry.get("tags", [])],
            "duration": entry.get("itunes_duration", ""),
            "episode": entry.get("itunes_episode", ""),
            "season": entry.get("itunes_season", ""),
            "explicit": entry.get("itunes_explicit", ""),
            "image": entry.get("image", {}).get("href", "") if "image" in entry else "",
            # Add a unique identifier for the episode
            "guid": entry.get("id", ""),
            # Add a hash of the audio URL if available
            "audio_url_hash": hashlib.md5(
                entry.get("enclosures", [{}])[0].get("href", "").encode()
            ).hexdigest()
            if entry.get("enclosures")
            else "",
        }

        # Save metadata to JSON file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        return True
    except Exception as e:
        print(f"Failed to save description: {e}")
        return False


def create_subdirectories(base_dir):
    """Create episode subdirectories"""
    episode_dir = os.path.join(base_dir, "episodes")
    os.makedirs(episode_dir, exist_ok=True)
    return episode_dir


def is_episode_downloaded(audio_path, desc_path, entry):
    """Check if episode is already downloaded by checking both audio and description files"""
    # Check if both files exist
    if os.path.exists(audio_path) and os.path.exists(desc_path):
        try:
            # If description file exists, check if it's the same episode by comparing GUID or URL hash
            with open(desc_path, "r", encoding="utf-8") as f:
                saved_metadata = json.load(f)

            # Get current episode identifiers
            current_guid = entry.get("id", "")
            current_url = (
                entry.get("enclosures", [{}])[0].get("href", "")
                if entry.get("enclosures")
                else ""
            )
            current_url_hash = (
                hashlib.md5(current_url.encode()).hexdigest() if current_url else ""
            )

            # Compare identifiers
            if (
                saved_metadata.get("guid") and saved_metadata["guid"] == current_guid
            ) or (
                saved_metadata.get("audio_url_hash")
                and saved_metadata["audio_url_hash"] == current_url_hash
            ):
                return True
        except:
            # If there's an error reading the description file, fall back to simple file existence check
            pass

    return False


def parse_rss_feed(feed_url, output_dir, limit=None, skip_existing=True):
    """Parse RSS feed and download podcast audio files"""
    print(f"Parsing RSS feed: {feed_url}")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create episodes directory
    episodes_dir = create_subdirectories(output_dir)

    # Parse RSS feed
    feed = feedparser.parse(feed_url)

    if feed.bozo:
        print(f"Warning: RSS feed parsing issue: {feed.bozo_exception}")

    # Get podcast title
    podcast_title = (
        feed.feed.title if hasattr(feed.feed, "title") else "Unknown Podcast"
    )
    print(f"Podcast: {podcast_title}")

    # Save podcast feed information
    podcast_info = {
        "title": podcast_title,
        "description": clean_html_text(feed.feed.get("description", "")),
        "link": feed.feed.get("link", ""),
        "language": feed.feed.get("language", ""),
        "author": feed.feed.get("author", ""),
        "image": feed.feed.get("image", {}).get("href", "")
        if hasattr(feed.feed, "image")
        else "",
        "copyright": feed.feed.get("rights", ""),
        "last_updated": feed.feed.get("updated", ""),
    }

    # Save podcast info to JSON file
    podcast_info_path = os.path.join(output_dir, "podcast_info.json")
    with open(podcast_info_path, "w", encoding="utf-8") as f:
        json.dump(podcast_info, f, ensure_ascii=False, indent=2)
    print(f"Saved podcast information to {podcast_info_path}")

    # Limit number of downloads
    entries = feed.entries[:limit] if limit else feed.entries

    # Counters
    downloaded = 0
    skipped = 0
    failed = 0
    transcoded = 0

    for i, entry in enumerate(entries):
        # Try to get audio URL
        enclosures = entry.get("enclosures", [])
        if not enclosures:
            print(f"Skipping entry {i + 1}: No audio attachment found")
            continue

        # Get first audio attachment
        audio_url = enclosures[0].get("href")
        if not audio_url:
            print(f"Skipping entry {i + 1}: Invalid audio URL")
            continue

        # Get title and publication date
        title = entry.get("title", f"episode_{i + 1}")

        # Create base filename (without extension)
        base_filename = sanitize_filename(f"{title}")

        # Create episode directory
        episode_dir = os.path.join(episodes_dir, base_filename)
        os.makedirs(episode_dir, exist_ok=True)

        # Create audio filename (always use .m4a extension)
        audio_filename = f"{base_filename}.m4a"
        audio_path = os.path.join(episode_dir, audio_filename)

        # Create description filename
        desc_filename = f"{base_filename}.json"
        desc_path = os.path.join(episode_dir, desc_filename)

        # Check if episode already exists
        if skip_existing and is_episode_downloaded(audio_path, desc_path, entry):
            print(
                f"Skipping entry {i + 1}: Episode already downloaded - {base_filename}"
            )
            skipped += 1
            continue

        # Download audio file to temporary location
        temp_path = os.path.join(episode_dir, "temp_download")
        print(f"Downloading entry {i + 1}: {title}")
        audio_success = download_file(audio_url, temp_path)

        # Save description
        desc_success = save_description(entry, desc_path)

        if audio_success:
            # Transcode to AAC
            try:
                print(f"Converting to AAC: {base_filename}")
                command = [
                    "ffmpeg",
                    "-i",
                    temp_path,
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                    "-y",
                    audio_path,
                ]
                result = subprocess.run(
                    command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )

                if result.returncode == 0:
                    downloaded += 1
                    transcoded += 1
                    print(f"Successfully converted and saved to: {audio_path}")
                else:
                    print(f"Conversion failed: {result.stderr}")
                    failed += 1
            except Exception as e:
                print(f"Conversion error: {e}")
                failed += 1
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        else:
            failed += 1

        if desc_success:
            print(
                f"Saved description to {os.path.join('episodes', base_filename, desc_filename)}"
            )

    # Print summary
    print("\nDownload Summary:")
    print(f"Total entries: {len(entries)}")
    print(f"Successfully downloaded and converted: {downloaded}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")


def main():
    parser = argparse.ArgumentParser(
        description="Download podcast audio from RSS feeds and convert to AAC format"
    )
    parser.add_argument("feed_url", help="RSS feed URL")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="downloads",
        help="Output directory (default: downloads)",
    )
    parser.add_argument(
        "-l", "--limit", type=int, help="Limit number of episodes to download"
    )
    parser.add_argument(
        "--no-skip", action="store_true", help="Do not skip existing files"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Download timeout in seconds (default: 30)",
    )

    args = parser.parse_args()

    try:
        parse_rss_feed(
            args.feed_url,
            args.output_dir,
            limit=args.limit,
            skip_existing=not args.no_skip,
        )
    except KeyboardInterrupt:
        print("\n程序被用户中断，正在退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
