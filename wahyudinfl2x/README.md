# WAHYUDINFLIX2

A web application for streaming movies and TV series built with Flask and featuring a custom streaming scraper.

## Features

- Browse latest movies and top TV series
- Search functionality for movies and series
- Detailed views for films with multiple player options
- Season and episode browsing for TV series
- Integrated video player for streaming content
- Responsive design for desktop and mobile

## Requirements

- Python 3.6+
- Flask
- requests
- beautifulsoup4
- lxml

## Installation

1. Clone the repository or download the source files
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you have the `streaming_scraper` module in the parent directory

## Running the Application

1. Navigate to the application directory:
   ```bash
   cd wahyudinfl2x
   ```

2. Run the Flask application:
   ```bash
   python app.py
   ```

3. Open your browser and go to `http://localhost:5000`

## Project Structure

```
wahyudinfl2x/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── script.js     # Client-side JavaScript
└── templates/
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── search.html       # Search page
    ├── search_results.html # Search results page
    ├── film_detail.html  # Film detail page
    ├── series_detail.html # Series detail page
    └── player.html       # Video player page
```

## API Endpoints

- `GET /` - Home page with latest content
- `GET /search` - Search interface
- `GET /film/<film_url>` - Film detail page
- `GET /series/<series_url>` - Series detail page
- `GET /player/<player_url>` - Video player page
- `GET /api/search` - Search API endpoint
- `GET /api/film/<film_url>` - Film data API
- `GET /api/series/<series_url>` - Series data API

## Usage

1. **Home Page**: Browse latest movies and top TV series
2. **Search**: Find specific movies or TV series by title
3. **Movie Details**: View movie information and available players
4. **Series Details**: Browse seasons and episodes with available players
5. **Video Player**: Watch content using the integrated player

## Legal Disclaimer

This application is for educational purposes only. The scraper accesses public streaming sites, but users should respect the terms of service of the target websites and applicable laws in their jurisdiction. The author is not responsible for any misuse of this code.