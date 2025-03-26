#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script: Download several popular podcasts
"""

import os
import subprocess
import sys
import logging
import datetime


# Setup logging
def setup_logging():
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(
        log_dir,
        f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_file


# Define some popular podcasts RSS feeds
PODCASTS = [
    {
        "name": "Lex Fridman",
        "rss": "https://lexfridman.com/feed/podcast/",
        "limit": 10,  # Only download the latest episode
    },
    {
        "name": "知行小酒馆",
        "rss": "http://www.ximalaya.com/album/46199233.xml",
        "limit": 10,
    },
    {
        "name": "The Joe Rogan Experience",
        "rss": "https://feeds.megaphone.fm/GLT1412515089",
        "limit": 10,
    },
    {
        "name": "后互联网时代的乱弹",
        "rss": "https://proxy.wavpub.com/pie.xml",
        "limit": 10,
    },
]


def main():
    # Setup logging
    log_file = setup_logging()
    logging.info("Starting podcast downloads")

    # Check if podcast_downloader.py exists
    if not os.path.exists("podcast_downloader.py"):
        logging.error("Error: podcast_downloader.py file not found")
        sys.exit(1)

    # Create separate directory for each podcast
    for podcast in PODCASTS:
        name = podcast["name"]
        rss = podcast["rss"]
        limit = podcast["limit"]

        logging.info(f"{'=' * 50}")
        logging.info(f"Downloading podcast: {name}")
        logging.info(f"RSS URL: {rss}")
        logging.info(f"Limit: Latest {limit} episodes")
        logging.info(f"{'=' * 50}")

        # Create output directory
        output_dir = os.path.join("/root/mydrive/podcasts", name)
        # output_dir = os.path.join("downloads", name)
        # Call podcast_downloader.py
        cmd = [
            sys.executable,
            "podcast_downloader.py",
            rss,
            "-o",
            output_dir,
            "-l",
            str(limit),
        ]

        try:
            logging.info(f"Executing command: {' '.join(cmd)}")
            result = subprocess.run(cmd, text=True, check=True)
            logging.info(f"Download successful: {name}")
            # Log output information
            if result.stdout:
                logging.info(f"Output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Download failed: {name}, exit code: {e.returncode}")
            if e.stdout:
                logging.error(f"Standard output: {e.stdout}")
            if e.stderr:
                logging.error(f"Error output: {e.stderr}")
        except Exception as e:
            logging.error(f"Unknown error occurred during download: {e}")

    logging.info("All download tasks completed!")
    logging.info(f"Log file saved at: {log_file}")


if __name__ == "__main__":
    main()
