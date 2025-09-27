from flask import Flask, render_template, request, jsonify
from streaming_scraper.scraper import StreamingScraper
import os
import threading
import time
import hashlib

app = Flask(__name__)
scraper = StreamingScraper()

# Add a custom function to generate player URLs safely
@app.template_global()
def player_url(url):
    """Generate a safe player URL"""
    import urllib.parse
    encoded_url = urllib.parse.quote(url, safe='/:?=&')
    return f"/player?url={encoded_url}"

# In-memory cache to store search results temporarily
cache = {}
CACHE_DURATION = 300  # 5 minutes

def is_cached_valid(url):
    """Check if cached data is still valid"""
    if url in cache:
        timestamp, data = cache[url]
        if time.time() - timestamp < CACHE_DURATION:
            return True
    return False

def get_cached_data(url):
    """Get cached data if still valid"""
    if is_cached_valid(url):
        return cache[url][1]
    return None

def cache_data(url, data):
    """Cache data with timestamp"""
    cache[url] = (time.time(), data)

@app.route('/')
def index():
    """Main page with search functionality"""
    # Get latest films and top series for the homepage
    latest_films = scraper.get_latest_films(1)[:10]
    top_series = scraper.get_top_series()[:10]
    return render_template('index.html', latest_films=latest_films, top_series=top_series)

@app.route('/search')
def search():
    """Search page"""
    query = request.args.get('q', '')
    media_type = request.args.get('type', 'all')
    
    if query:
        results = scraper.search(query, media_type)
        return render_template('search_results.html', results=results, query=query)
    else:
        return render_template('search.html')

@app.route('/film/<path:film_url>')
def film_detail(film_url):
    """Film detail page"""
    # Reconstruct the full URL since it's passed as a path
    full_url = f"https://tv12.lk21official.life/{film_url}"
    
    # Check if data is cached
    cached_data = get_cached_data(full_url)
    if cached_data:
        film_data = cached_data
    else:
        film_data = scraper.scrape_film(full_url)
        cache_data(full_url, film_data)
    
    return render_template('film_detail.html', film=film_data)

@app.route('/series/<path:series_url>')
def series_detail(series_url):
    """Series detail page"""
    # Reconstruct the full URL since it's passed as a path
    full_url = f"https://tv1.nontondrama.my/{series_url}"
    
    # Check if data is cached
    cached_data = get_cached_data(full_url)
    if cached_data:
        series_data = cached_data
    else:
        series_data = scraper.scrape_series(full_url)
        cache_data(full_url, series_data)
    
    return render_template('series_detail.html', series=series_data)

@app.route('/api/search')
def api_search():
    """API endpoint for search"""
    query = request.args.get('q', '')
    media_type = request.args.get('type', 'all')
    
    if query:
        results = scraper.search(query, media_type)
        return jsonify(results)
    else:
        return jsonify([])

@app.route('/api/film/<path:film_url>')
def api_film_detail(film_url):
    """API endpoint for film data"""
    full_url = f"https://tv12.lk21official.life/{film_url}"
    film_data = scraper.scrape_film(full_url)
    return jsonify(film_data)

@app.route('/api/series/<path:series_url>')
def api_series_detail(series_url):
    """API endpoint for series data"""
    full_url = f"https://tv1.nontondrama.my/{series_url}"
    series_data = scraper.scrape_series(full_url)
    return jsonify(series_data)

from urllib.parse import unquote

@app.route('/player')
def player():
    """Player page - redirects to the actual player URL or shows embed option"""
    player_url = request.args.get('url', '')
    # Flask automatically URL-decodes query parameters, but if there are nested parameters 
    # they might still be encoded
    
    # Decode the URL to handle potential double encoding
    decoded_url = unquote(player_url)
    
    # Check if this looks like a double-encoded URL and decode again if needed
    if '%3D' in decoded_url or '%3F' in decoded_url or '%26' in decoded_url:
        decoded_url = unquote(decoded_url)
    
    # Validate the URL to ensure it's from the expected domain
    if decoded_url.startswith('https://playeriframe.sbs/iframe.php?url='):
        # Option to redirect directly to the player URL (which should work better with CSP)
        if request.args.get('redirect', 'false').lower() == 'true':
            from flask import redirect
            return redirect(decoded_url)
        else:
            # Still allow embedding for cases where it works
            return render_template('player.html', player_url=decoded_url)
    else:
        # If it doesn't start with the expected domain, don't allow it
        # This is a security measure to prevent arbitrary URL loading
        return render_template('player.html', player_url='')

@app.route('/extract', methods=['GET', 'POST'])
def extract_url():
    """Page to extract content from user-provided URLs"""
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        if url:
            try:
                result = scraper.scrape_from_user_url(url)
                return render_template('extract_result.html', result=result, input_url=url)
            except Exception as e:
                error_result = {
                    'error': f'Error scraping URL: {str(e)}',
                    'url': url
                }
                return render_template('extract_result.html', result=error_result, input_url=url)
    
    return render_template('extract.html')

@app.route('/api/extract', methods=['POST'])
def api_extract_url():
    """API endpoint to extract content from user-provided URL"""
    data = request.get_json()
    url = data.get('url', '') if data else ''
    
    if url:
        try:
            result = scraper.scrape_from_user_url(url)
            return jsonify(result)
        except Exception as e:
            return jsonify({
                'error': str(e),
                'url': url
            })
    else:
        return jsonify({'error': 'No URL provided'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)