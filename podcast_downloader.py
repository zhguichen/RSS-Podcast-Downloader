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

def sanitize_filename(filename):
    """Clean filename by removing illegal characters"""
    # Replace characters not allowed in Windows and Unix filenames
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def download_file(url, output_path):
    """Download file with progress bar"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Ensure request was successful
        
        # Get file size (if provided by server)
        total_size = int(response.headers.get('content-length', 0))
        
        # Create progress bar
        with open(output_path, 'wb') as f, tqdm(
            desc=os.path.basename(output_path),
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    f.write(chunk)
                    bar.update(len(chunk))
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        # Remove partially downloaded file if download fails
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

def save_description(entry, output_path):
    """Save podcast episode description and metadata to a JSON file"""
    try:
        # Extract relevant metadata
        metadata = {
            "title": entry.get("title", ""),
            "description": entry.get("description", ""),
            "summary": entry.get("summary", ""),
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
            "audio_url_hash": hashlib.md5(entry.get("enclosures", [{}])[0].get("href", "").encode()).hexdigest() if entry.get("enclosures") else ""
        }
        
        # Save metadata to JSON file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"Failed to save description: {e}")
        return False

def create_subdirectories(base_dir):
    """Create audio and description subdirectories"""
    audio_dir = os.path.join(base_dir, "audio")
    desc_dir = os.path.join(base_dir, "description")
    
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(desc_dir, exist_ok=True)
    
    return audio_dir, desc_dir

def is_episode_downloaded(audio_path, desc_path, entry):
    """Check if episode is already downloaded by checking both audio and description files"""
    # Check if both files exist
    if os.path.exists(audio_path) and os.path.exists(desc_path):
        try:
            # If description file exists, check if it's the same episode by comparing GUID or URL hash
            with open(desc_path, 'r', encoding='utf-8') as f:
                saved_metadata = json.load(f)
            
            # Get current episode identifiers
            current_guid = entry.get("id", "")
            current_url = entry.get("enclosures", [{}])[0].get("href", "") if entry.get("enclosures") else ""
            current_url_hash = hashlib.md5(current_url.encode()).hexdigest() if current_url else ""
            
            # Compare identifiers
            if (saved_metadata.get("guid") and saved_metadata["guid"] == current_guid) or \
               (saved_metadata.get("audio_url_hash") and saved_metadata["audio_url_hash"] == current_url_hash):
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
    
    # Create audio and description subdirectories
    audio_dir, desc_dir = create_subdirectories(output_dir)
    
    # Parse RSS feed
    feed = feedparser.parse(feed_url)
    
    if feed.bozo:
        print(f"Warning: RSS feed parsing issue: {feed.bozo_exception}")
    
    # Get podcast title
    podcast_title = feed.feed.title if hasattr(feed.feed, 'title') else "Unknown Podcast"
    print(f"Podcast: {podcast_title}")
    
    # Save podcast feed information
    podcast_info = {
        "title": podcast_title,
        "description": feed.feed.get("description", ""),
        "link": feed.feed.get("link", ""),
        "language": feed.feed.get("language", ""),
        "author": feed.feed.get("author", ""),
        "image": feed.feed.get("image", {}).get("href", "") if hasattr(feed.feed, "image") else "",
        "copyright": feed.feed.get("rights", ""),
        "last_updated": feed.feed.get("updated", "")
    }
    
    # Save podcast info to JSON file
    podcast_info_path = os.path.join(desc_dir, "podcast_info.json")
    with open(podcast_info_path, 'w', encoding='utf-8') as f:
        json.dump(podcast_info, f, ensure_ascii=False, indent=2)
    print(f"Saved podcast information to {podcast_info_path}")
    
    # Limit number of downloads
    entries = feed.entries[:limit] if limit else feed.entries
    
    # Counters
    downloaded = 0
    skipped = 0
    failed = 0
    
    for i, entry in enumerate(entries):
        # Try to get audio URL
        enclosures = entry.get('enclosures', [])
        if not enclosures:
            print(f"Skipping entry {i+1}: No audio attachment found")
            continue
        
        # Get first audio attachment
        audio_url = enclosures[0].get('href')
        if not audio_url:
            print(f"Skipping entry {i+1}: Invalid audio URL")
            continue
        
        # Get title and publication date
        title = entry.get('title', f"episode_{i+1}")
        published = entry.get('published', '')
        
        # Extract year-month-day from publication date (if available)
        date_prefix = ""
        if published:
            try:
                # Try to parse time string, format may vary by RSS feed
                time_struct = entry.get('published_parsed')
                if time_struct:
                    date_prefix = time.strftime("%Y%m%d_", time_struct)
            except:
                pass
        
        # Determine file extension
        parsed_url = urlparse(audio_url)
        path = parsed_url.path
        extension = os.path.splitext(path)[1]
        if not extension:
            # If no extension in URL, default to .mp3
            extension = ".mp3"
        
        # Create base filename (without extension)
        base_filename = sanitize_filename(f"{date_prefix}{title}")
        
        # Create audio filename
        audio_filename = f"{base_filename}{extension}"
        audio_path = os.path.join(audio_dir, audio_filename)
        
        # Create description filename
        desc_filename = f"{base_filename}.json"
        desc_path = os.path.join(desc_dir, desc_filename)
        
        # Check if episode already exists
        if skip_existing and is_episode_downloaded(audio_path, desc_path, entry):
            print(f"Skipping entry {i+1}: Episode already downloaded - {base_filename}")
            skipped += 1
            continue
        
        # Download audio file
        print(f"Downloading entry {i+1}: {title}")
        audio_success = download_file(audio_url, audio_path)
        
        # Save description
        desc_success = save_description(entry, desc_path)
        
        if audio_success:
            downloaded += 1
            print(f"Saved audio to {os.path.join('audio', audio_filename)}")
            print(f"Saved description to {os.path.join('description', desc_filename)}")
        else:
            failed += 1
    
    # Print summary
    print("\nDownload Summary:")
    print(f"Total entries: {len(entries)}")
    print(f"Successfully downloaded: {downloaded}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")

def main():
    parser = argparse.ArgumentParser(description='Download podcast audio from RSS feeds')
    parser.add_argument('feed_url', help='RSS feed URL')
    parser.add_argument('-o', '--output-dir', default='downloads', help='Output directory (default: downloads)')
    parser.add_argument('-l', '--limit', type=int, help='Limit number of episodes to download')
    parser.add_argument('--no-skip', action='store_true', help='Do not skip existing files')
    
    args = parser.parse_args()
    
    parse_rss_feed(
        args.feed_url, 
        args.output_dir, 
        limit=args.limit, 
        skip_existing=not args.no_skip
    )

if __name__ == "__main__":
    main() 