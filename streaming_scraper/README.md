# Streaming Site Scraper

A Python web scraper for Indonesian streaming websites that extracts information about films and TV series, including embedded player links.

## Features

- **Film Scraping**: Extracts film title and embedded player links (P2P, TURBOVIP, CAST, HYDRAX)
- **Series Scraping**: Extracts series title, seasons, episodes, and embedded player links for each episode
- **Latest Films**: Fetches the latest films from the streaming site
- **Top Series**: Fetches the top series from the streaming site
- **Search Functionality**: Search for films and series by title
- **Unified Scraping**: Automatically detects and scrapes film or series based on URL

## Supported Sites

- Film site: `https://tv12.lk21official.life/`
- Series site: `https://tv1.nontondrama.my/`

## Installation

1. Install required packages:
```bash
pip install requests beautifulsoup4 lxml
```

2. Clone the repository or create the scraper files as per the project structure.

## Usage

### Basic Usage

```python
from scraper import StreamingScraper
import json

scraper = StreamingScraper()

# Scrape a specific film
film_data = scraper.scrape_film('https://tv12.lk21official.life/sirat-2025')
print(json.dumps(film_data, indent=2))

# Scrape a specific series
series_data = scraper.scrape_series('https://tv1.nontondrama.my/alice-in-borderland-2020')
print(json.dumps(series_data, indent=2))

# Get latest films
latest_films = scraper.get_latest_films(1)
for film in latest_films:
    print(f"- {film['title']}: {film['url']}")

# Search for content
search_results = scraper.search('Alice')
for result in search_results:
    print(f"- {result['type']}: {result['title']}: {result['url']}")
```

### Interactive Usage

Run the main application for interactive mode:

```bash
python main.py
```

## Functions

### `scrape_film(film_url)`
Scrapes a film page and returns:
- Film title
- Embedded player links (P2P, TURBOVIP, CAST, HYDRAX)

### `scrape_series(series_url)`
Scrapes a series page and returns:
- Series title
- Seasons with episodes
- Embedded player links for each episode

### `scrape_episode(episode_url)`
Scrapes an episode page and returns:
- Episode title
- Embedded player links

### `get_latest_films(page=1)`
Returns a list of latest films from the specified page.

### `get_top_series()`
Returns a list of top series from the website.

### `search(query, media_type='all')`
Searches for films or series by title.
- `media_type`: 'film', 'series', or 'all' (default)

### `scrape_any(url)`
Unified function that automatically detects whether the URL is for a film or series and scrapes accordingly.

## Output Format

The scraper returns data in the following JSON format:

### Film:
```json
{
  "type": "film",
  "title": "Film Title",
  "url": "https://...",
  "players": {
    "P2P": "https://player-url...",
    "TURBOVIP": "https://player-url...",
    "CAST": "https://player-url...",
    "HYDRAX": "https://player-url..."
  }
}
```

### Series:
```json
{
  "type": "series",
  "title": "Series Title",
  "url": "https://...",
  "episodes": {
    "Season 1": {
      "Episode 1": {
        "title": "Episode Title",
        "url": "https://...",
        "players": {
          "P2P": "https://player-url...",
          "TURBOVIP": "https://player-url...",
          "CAST": "https://player-url...",
          "HYDRAX": "https://player-url..."
        }
      }
    }
  }
}
```

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- lxml

## Legal Disclaimer

This scraper is intended for educational purposes only. Please respect the terms of service of the target websites and applicable laws in your jurisdiction. The author is not responsible for any misuse of this code.

## Notes

- The scraper may need updates if the target websites change their structure
- Implement rate limiting when making multiple requests to avoid being blocked
- Some content may be geo-restricted