# 项目名称

[Chinese](README_zh.md) | 中文


# RSS Podcast Downloader

A simple Python script for downloading podcast audio files from RSS feeds.

## Features

- Parse podcast episodes from RSS feeds
- Download podcast audio files
- Display download progress bar
- Automatically skip already downloaded files
- Support for limiting the number of downloads
- Filenames include publication date and title
- Support for importing podcast lists from OPML files
- Support for concurrent downloading of multiple podcasts
- Save podcast descriptions and metadata in JSON format
- Organize downloads into audio and description folders
- Smart duplicate detection using episode identifiers

## Installation

1. Make sure you have Python 3.6 or higher installed
2. Clone or download this repository
3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Download all episodes from a single podcast:

```bash
python podcast_downloader.py https://example.com/podcast.xml
```

This will download all podcast episodes from the specified RSS feed to the `downloads` directory.

### Command Line Options

- `-o, --output-dir`: Specify output directory (default: `downloads`)
- `-l, --limit`: Limit the number of episodes to download
- `--no-skip`: Do not skip existing files

### Example

Download the latest 5 episodes to a custom directory:

```bash
python podcast_downloader.py https://example.com/podcast.xml -o my_podcasts -l 5
```

### Using the Example Script

We provide an example script that can download several popular podcasts:

```bash
python example.py
```


## Saved Metadata

For each podcast, the following directory structure is created:

```
downloads/
├── audio/
│   ├── 20230101_Episode1.mp3
│   ├── 20230108_Episode2.mp3
│   └── ...
└── description/
    ├── podcast_info.json
    ├── 20230101_Episode1.json
    ├── 20230108_Episode2.json
    └── ...
```

The metadata files contain detailed information about each episode, including:
- Title
- Description
- Summary
- Publication date
- Author
- Duration
- Episode number
- Season number
- Tags
- Image URL
- Unique identifiers (GUID and audio URL hash)

## Common RSS Feed Examples

Here are some RSS feed URLs for popular podcasts:



- **Podcast Index**: Browse the directory at https://podcastindex.org/ to find RSS feeds for thousands of podcasts
- **Xiaoyuzhou FM**: Find the podcast in the Xiaoyuzhou App, share the link, then open it in a browser to locate the RSS feed URL
- **Spotify**: Spotify doesn't provide RSS feeds directly, but you can use third-party services to find equivalent RSS feeds
- **Google Podcasts**: Copy the podcast URL and use converter tools to find the corresponding RSS feed

## Notes

- Please respect content creators' copyright
- Downloaded files are for personal use only
- Some RSS feeds may require authentication or have access restrictions # RSS-Podcast-Downloader
