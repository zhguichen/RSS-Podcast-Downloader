#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Example script: Download several popular podcasts
"""

import os
import subprocess
import sys

# Define some popular podcasts RSS feeds
PODCASTS = [
    {
        "name": "Lex Fridman",
        "rss": "https://lexfridman.com/feed/podcast/",
        "limit": 3  # Only download the latest 3 episodes
    },
    {
        "name": "知行小酒馆",
        "rss": "http://www.ximalaya.com/album/46199233.xml",
        "limit": 3
    },
    {
        "name": "The Joe Rogan Experience",
        "rss": "https://feeds.megaphone.fm/GLT1412515089",
        "limit": 2
    },
    {
        "name": "后互联网时代的乱弹",
        "rss": "https://proxy.wavpub.com/pie.xml",
        "limit": 3
    }
]

def main():
    # Check if podcast_downloader.py exists
    if not os.path.exists("podcast_downloader.py"):
        print("Error: podcast_downloader.py file not found")
        sys.exit(1)
    
    # Check if dependencies are installed
    try:
        import feedparser
        import requests
        from tqdm import tqdm
    except ImportError:
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Create separate directory for each podcast
    for podcast in PODCASTS:
        name = podcast["name"]
        rss = podcast["rss"]
        limit = podcast["limit"]
        
        print(f"\n{'='*50}")
        print(f"Downloading podcast: {name}")
        print(f"RSS feed: {rss}")
        print(f"Limit: Latest {limit} episodes")
        print(f"{'='*50}\n")
        
        # Create output directory
        output_dir = os.path.join("downloads", name)
        
        # Call podcast_downloader.py
        cmd = [
            sys.executable,
            "podcast_downloader.py",
            rss,
            "-o", output_dir,
            "-l", str(limit)
        ]
        
        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"Download failed: {e}")
    
    print("\nAll downloads completed!")

if __name__ == "__main__":
    main() 