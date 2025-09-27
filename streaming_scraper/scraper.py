import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin
from typing import Dict, List, Optional


class StreamingScraper:
        
    def scrape_film(self, film_url: str) -> Dict:
        """
        Scrape information from a film page
        Returns: Dictionary with film title, thumbnail and embedded player links
        """
        try:
            response = self.session.get(film_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract film title from the page title
            title = soup.title.string if soup.title else ""
            # Clean up the title to extract just the film name
            if "|" in title:
                title = title.split("|")[0].strip()
            
            # Generate a dummy thumbnail
            from urllib.parse import quote
            thumbnail = f"https://placehold.co/200x280/181818/FFFFFF?text={quote(title)}"
            
            # Find player links
            all_links = soup.find_all('a', href=True)
            player_links = {}
            
            for link in all_links:
                link_text = link.get_text().strip()
                if any(keyword in link_text.upper() for keyword in ['P2P', 'TURBO', 'CAST', 'HYDRAX']):
                    player_links[link_text] = link['href']
            
            return {
                'type': 'film',
                'title': title,
                'url': film_url,
                'thumbnail': thumbnail,
                'players': player_links
            }
        except Exception as e:
            print(f"Error scraping film {film_url}: {str(e)}")
            return {
                'type': 'film',
                'title': '',
                'url': film_url,
                'thumbnail': '',
                'players': {},
                'error': str(e)
            }
    
    def scrape_series(self, series_url: str) -> Dict:
        """
        Scrape information from a series page - enhanced to get all seasons and episodes from JSON data
        Returns: Dictionary with series title, thumbnail, seasons, episodes, and embedded player links
        """
        try:
            response = self.session.get(series_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract series title
            title = soup.title.string if soup.title else ""
            if "|" in title:
                title = title.split("|")[0].strip()
            
            # Generate a dummy thumbnail
            from urllib.parse import quote
            thumbnail = f"https://placehold.co/200x280/181818/FFFFFF?text={quote(title)}"
            
            episodes_data = {}
            
            # Extract season data from JSON script tag
            import re
            import json
            
            season_data_script = soup.find('script', id='season-data')
            if season_data_script:
                # Get the content of the script tag
                script_content = season_data_script.string
                if script_content:
                    # The script tag might contain other content, extract just the JSON part
                    # Remove script tags and try to find the JSON
                    content = script_content.strip()
                    # Handle the case where the JSON is wrapped in CDATA or comments
                    content = content.replace('<!--', '').replace('-->', '').strip()
                    
                    # Find JSON object within the content
                    # Look for content between first { and last }
                    first_brace = content.find('{')
                    last_brace = content.rfind('}')
                    
                    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                        json_text = content[first_brace:last_brace+1]
                        
                        try:
                            season_data = json.loads(json_text)
                            
                            # Loop through all seasons and episodes from the JSON data
                            for season_num, episodes in season_data.items():
                                season_key = f'Season {season_num}'
                                if season_key not in episodes_data:
                                    episodes_data[season_key] = {}
                                
                                for episode_info in episodes:
                                    episode_num = episode_info.get('episode_no', 'unknown')
                                    episode_slug = episode_info.get('slug', '')
                                    
                                    if episode_slug:
                                        # Build the full episode URL
                                        episode_url = f'https://tv1.nontondrama.my/{episode_slug}'
                                        
                                        # Scrape episode details to get player links
                                        episode_detail = self.scrape_episode(episode_url)
                                        
                                        episode_key = f'Episode {episode_num}'
                                        episodes_data[season_key][episode_key] = episode_detail
                        except json.JSONDecodeError as e:
                            print(f"Could not parse season JSON data: {e}")
                            # Print a sample of the problematic JSON for debugging
                            print(f"Problematic JSON text: {json_text[:200]}...")
            
            # If we couldn't get data from JSON, fall back to the original approach
            if not episodes_data:
                # Find all possible episode links on the page 
                all_links = soup.find_all('a', href=True)
                episode_urls = set()
                
                for link in all_links:
                    href = link['href']
                    link_text = link.get_text().strip()
                    
                    # Look for episode-related URLs
                    if any(keyword in href.lower() for keyword in ['episode', 'eps']):
                        if href.startswith('/'):
                            full_url = 'https://tv1.nontondrama.my' + href
                        else:
                            full_url = href
                        
                        # Only add if it's a real episode URL
                        if any(keyword in full_url.lower() for keyword in ['episode']):
                            episode_urls.add((link_text, full_url))
                
                # Extract season/episode info and scrape each episode
                for episode_text, episode_url in episode_urls:
                    episode_detail = self.scrape_episode(episode_url)
                    
                    # Extract season and episode number from the URL or text
                    season_episode_info = self._extract_season_episode(episode_text, episode_url)
                    
                    if not season_episode_info:
                        # If not found in link text, try to extract from episode URL or title
                        season_episode_info = self._extract_season_episode(episode_detail.get('title', ''), episode_url)
                    
                    if season_episode_info:
                        season_num = season_episode_info.get('season', 'unknown')
                        episode_num = season_episode_info.get('episode', 'unknown')
                        
                        season_key = f'Season {season_num}'
                        episode_key = f'Episode {episode_num}'
                    else:
                        # If we still can't determine season/episode, put in a default season
                        season_key = 'Season 1'
                        episode_key = episode_detail.get('title', f'Episode from {episode_url.split("/")[-1]}')
                    
                    if season_key not in episodes_data:
                        episodes_data[season_key] = {}
                    
                    episodes_data[season_key][episode_key] = episode_detail
            
            return {
                'type': 'series',
                'title': title,
                'url': series_url,
                'thumbnail': thumbnail,
                'episodes': episodes_data
            }
        except Exception as e:
            print(f"Error scraping series {series_url}: {str(e)}")
            return {
                'type': 'series',
                'title': '',
                'url': series_url,
                'thumbnail': '',
                'episodes': {},
                'error': str(e)
            }
    
    def scrape_episode(self, episode_url: str) -> Dict:
        """
        Scrape information from an episode page
        Returns: Dictionary with episode title and embedded player links
        """
        try:
            response = self.session.get(episode_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract episode title
            title = soup.title.string if soup.title else ""
            if "|" in title:
                title = title.split("|")[0].strip()
            
            # Find player links
            all_links = soup.find_all('a', href=True)
            player_links = {}
            
            for link in all_links:
                link_text = link.get_text().strip()
                if any(keyword in link_text.upper() for keyword in ['P2P', 'TURBO', 'CAST', 'HYDRAX']):
                    player_links[link_text] = link['href']
            
            return {
                'title': title,
                'url': episode_url,
                'players': player_links
            }
        except Exception as e:
            print(f"Error scraping episode {episode_url}: {str(e)}")
            return {
                'title': '',
                'url': episode_url,
                'players': {},
                'error': str(e)
            }
    
    def _extract_season_episode(self, episode_text: str, episode_url: str) -> Optional[Dict]:
        """
        Extract season and episode numbers from text or URL
        """
        import re
        
        # Try to extract from episode_text first
        season_match = re.search(r'Season\s+(\d+)', episode_text, re.IGNORECASE)
        episode_match = re.search(r'Episode\s+(\d+)', episode_text, re.IGNORECASE)
        
        if not season_match:
            season_match = re.search(r'S\.(\d+)', episode_text)
        if not episode_match:
            episode_match = re.search(r'E\.(\d+)', episode_text)
        
        # If not found in text, try URL
        if not season_match or not episode_match:
            season_match = re.search(r'season[-_]?(\d+)', episode_url, re.IGNORECASE)
            episode_match = re.search(r'episode[-_]?(\d+)', episode_url, re.IGNORECASE)
        
        if not season_match:
            season_match = re.search(r's(\d+)', episode_url)
        if not episode_match:
            episode_match = re.search(r'e(\d+)', episode_url)
        
        result = {}
        if season_match:
            result['season'] = season_match.group(1)
        if episode_match:
            result['episode'] = episode_match.group(1)
        
        return result if result else None
    
    def get_latest_films(self, page: int = 1) -> List[Dict]:
        """
        Get list of latest films from the main page with thumbnails
        """
        try:
            film_url = f'https://tv12.lk21official.life/latest/page/{page}'
            response = self.session.get(film_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find film links and thumbnails
            film_elements = soup.find_all('article')
            films = []
            
            for item in film_elements:
                link = item.find('a', href=True)
                if link:
                    relative_url = link['href']
                    if not relative_url.startswith('http'):
                        relative_url = 'https://tv12.lk21official.life' + relative_url
                    
                    title = link.get_text().strip()
                    # Generate a dummy thumbnail
                    from urllib.parse import quote
                    thumbnail = f"https://placehold.co/200x280/181818/FFFFFF?text={quote(title)}"
                    
                    films.append({
                        'title': title,
                        'url': relative_url,
                        'thumbnail': thumbnail
                    })
            
            return films
        except Exception as e:
            print(f"Error getting latest films: {str(e)}")
            return []
    
    def __init__(self):
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # TMDB API details - using public API key
        self.tmdb_api_key = "f3a2f3e5a3b463e5c2b6d4a4a7c7f3c7"  # Free TMDB API key
        self.tmdb_base_url = "https://api.themoviedb.org/3"
        self.tmdb_image_base_url = "https://image.tmdb.org/t/p/w500"
    
    def search_tmdb(self, query: str, media_type: str = 'multi') -> List[Dict]:
        """
        Search for content on TMDB
        """
        try:
            search_url = f"{self.tmdb_base_url}/search/{media_type}"
            params = {
                'api_key': self.tmdb_api_key,
                'query': query
            }
            response = self.session.get(search_url, params=params)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            return []
        except Exception as e:
            print(f"Error searching TMDB: {str(e)}")
            return []
    
    def get_tmdb_poster(self, title: str, media_type: str = 'multi') -> str:
        """
        Get poster URL from TMDB based on title
        """
        try:
            # Clean the title to improve search
            clean_title = re.sub(r'\s*\(\d{4}\).*', '', title)  # Remove year and other info
            clean_title = clean_title.strip()
            
            if not clean_title:
                return ""
            
            results = self.search_tmdb(clean_title, media_type)
            
            # Find the best match based on title similarity
            best_match = None
            best_score = 0
            
            for result in results:
                result_title = result.get('title') or result.get('name', '')
                similarity = self._calculate_title_similarity(clean_title.lower(), result_title.lower())
                
                if similarity > best_score and similarity > 0.7:  # 70% similarity threshold
                    best_score = similarity
                    best_match = result
            
            if best_match:
                poster_path = best_match.get('poster_path')
                if poster_path:
                    return f"{self.tmdb_image_base_url}{poster_path}"
            
            return ""
        except Exception as e:
            print(f"Error getting TMDB poster for {title}: {str(e)}")
            return ""
    
    def _calculate_title_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate similarity between two strings
        """
        # Simple word-based similarity
        words1 = set(re.findall(r'\w+', s1.lower()))
        words2 = set(re.findall(r'\w+', s2.lower()))
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def get_top_series(self) -> List[Dict]:
        """
        Get list of top series from the main series page with thumbnails
        """
        try:
            series_url = 'https://tv1.nontondrama.my/top-series-today'
            response = self.session.get(series_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find series links and thumbnails
            series_elements = soup.find_all('article')
            series_list = []
            
            for item in series_elements:
                link = item.find('a', href=True)
                if link:
                    relative_url = link['href']
                    if not relative_url.startswith('http'):
                        relative_url = 'https://tv1.nontondrama.my' + relative_url
                    
                    title = link.get_text().strip()
                    # Generate a dummy thumbnail
                    from urllib.parse import quote
                    thumbnail = f"https://placehold.co/200x280/181818/FFFFFF?text={quote(title)}"
                    
                    series_list.append({
                        'title': link.get_text().strip(),
                        'url': relative_url,
                        'thumbnail': thumbnail
                    })
            
            return series_list
        except Exception as e:
            print(f"Error getting top series: {str(e)}")
            return []
    
    def search(self, query: str, media_type: str = 'all') -> List[Dict]:
        """
        Enhanced search functionality with more comprehensive coverage
        """
        results_map = {}  # Use a dict to prevent duplicates (key: url, value: result)
        query_lower = query.lower()
        
        # Expanded search - check multiple pages for films with extended range
        if media_type in ['all', 'film']:
            # Check many pages of latest films for better coverage
            for page in range(1, 21):  # Check first 20 pages for better coverage
                latest_films = self.get_latest_films(page)
                if not latest_films:  # If no more films, break
                    break
                
                for film in latest_films:
                    title_lower = film['title'].lower()
                    # Enhanced matching with multiple criteria
                    if (
                        query_lower in title_lower or 
                        self._is_close_match(query_lower, title_lower) or
                        self._fuzzy_match(query_lower, title_lower)
                    ):
                        # Calculate score and add to results map to avoid duplicates
                        score = self._calculate_match_score(query_lower, title_lower)
                        # Boost score for exact matches (case-insensitive)
                        if query_lower == title_lower:
                            score += 100
                        # Use URL as key to avoid duplicates
                        results_map[film['url']] = {
                            'type': 'film',
                            'title': film['title'],
                            'url': film['url'],
                            'score': score
                        }
            
            # Also search in genre pages for more comprehensive coverage
            # Get list of genres and search few pages in each
            try:
                genre_response = self.session.get('https://tv12.lk21official.life/latest/page/1')
                genre_soup = BeautifulSoup(genre_response.content, 'html.parser')
                
                # Find genre links
                genre_links = genre_soup.find_all('a', href=True)
                genres_found = []
                
                for link in genre_links:
                    href = link['href']
                    text = link.get_text().strip()
                    if '/genre/' in href and text and text not in ['HOME', 'LAINNYA']:
                        genres_found.append((text, href))
                
                # Search in first 5 genres for extra content
                for genre_name, genre_path in genres_found[:5]:
                    for page in range(1, 4):  # Search first 3 pages of each genre
                        genre_url = f"https://tv12.lk21official.life{genre_path}/page/{page}"
                        try:
                            genre_response = self.session.get(genre_url)
                            if genre_response.status_code != 200:
                                break
                                
                            genre_soup = BeautifulSoup(genre_response.content, 'html.parser')
                            film_elements = genre_soup.find_all('article')
                            
                            for item in film_elements:
                                link = item.find('a', href=True)
                                if link:
                                    relative_url = link['href']
                                    if not relative_url.startswith('http'):
                                        relative_url = 'https://tv12.lk21official.life' + relative_url
                                    
                                    title = link.get_text().strip()
                                    title_lower = title.lower()
                                    
                                    if (
                                        query_lower in title_lower or 
                                        self._is_close_match(query_lower, title_lower)
                                    ):
                                        score = self._calculate_match_score(query_lower, title_lower)
                                        results_map[relative_url] = {
                                            'type': 'film',
                                            'title': title,
                                            'url': relative_url,
                                            'score': score
                                        }
                        except:
                            continue  # Skip if there's an error with a genre page
            except:
                pass  # Continue with just the main search if genre search fails
        
        # Expanded search for series
        if media_type in ['all', 'series']:
            # Check multiple series pages (though may be limited)
            # For series, we need to check the main series listing pages
            for page in [1]:  # Series may not have pagination like films
                series_list = self.get_top_series_page(page)
                
                if series_list:
                    for series in series_list:
                        title_lower = series['title'].lower()
                        if (
                            query_lower in title_lower or 
                            self._is_close_match(query_lower, title_lower) or
                            self._fuzzy_match(query_lower, title_lower)
                        ):
                            # Calculate score and add to results map to avoid duplicates
                            score = self._calculate_match_score(query_lower, title_lower)
                            # Boost score for exact matches (case-insensitive)
                            if query_lower == title_lower:
                                score += 100
                            # Use URL as key to avoid duplicates
                            results_map[series['url']] = {
                                'type': 'series',
                                'title': series['title'],
                                'url': series['url'],
                                'score': score
                            }
        
        # Convert map to list and sort
        results = list(results_map.values())
        # Sort results by score (higher scores first) then by title
        results.sort(key=lambda x: (-x.get('score', 0), x['title']))
        
        # Remove score from final results (just used for sorting)
        for result in results:
            result.pop('score', None)
        
        return results

    def _fuzzy_match(self, query: str, title: str) -> bool:
        """
        Simple fuzzy matching to catch typos and variations
        """
        # Only use fuzzy matching for queries longer than 3 characters to reduce false positives
        if len(query) < 4:
            return False
            
        # Simple approach: check if most characters of query appear in title in order
        query_clean = ''.join(c for c in query if c.isalnum()).lower()
        title_clean = ''.join(c for c in title if c.isalnum()).lower()
        
        if not query_clean or not title_clean or len(query_clean) < 3:
            return False
            
        # Count how many characters of query appear in the title in sequence
        pos = 0
        matches = 0
        for char in query_clean:
            found = False
            for i in range(pos, len(title_clean)):
                if title_clean[i] == char:
                    pos = i + 1
                    matches += 1
                    found = True
                    break
            if not found:
                break
                
        # If more than 70% of the query characters were found in sequence, it's a potential match
        return matches >= len(query_clean) * 0.7

    def _is_close_match(self, query: str, title: str) -> bool:
        """
        Check if query is a close match to title using more sophisticated matching
        """
        import re
        
        # Clean the strings to remove special characters for comparison
        clean_query = re.sub(r'[^\w\s]', ' ', query.lower()).strip()
        clean_title = re.sub(r'[^\w\s]', ' ', title.lower()).strip()
        
        # Split into words
        query_words = [word for word in clean_query.split() if word]
        title_words = [word for word in clean_title.split() if word]
        
        if not query_words:
            return False
            
        matches = 0
        for q_word in query_words:
            for t_word in title_words:
                # Exact word match
                if q_word == t_word:
                    matches += 1
                    break
                # Check for approximate matches (for typos)
                elif self._words_approximate_match(q_word, t_word):
                    matches += 1
                    break
        
        # If all query words match, or at least 75% of them match, consider it a close match
        return matches == len(query_words) or matches >= len(query_words) * 0.75
    
    def _words_approximate_match(self, word1: str, word2: str) -> bool:
        """
        Check if two words are approximately the same (for handling typos)
        """
        # Simple approach: check if one word is contained in another or they're similar
        if word1 in word2 or word2 in word1:
            # Make sure it's a significant portion, not just a common substring
            longer = max(len(word1), len(word2))
            shorter = min(len(word1), len(word2))
            if longer <= 3:  # For short words, direct containment is enough
                return True
            return shorter / longer >= 0.6  # 60% of shorter word should match longer
        
        # For longer words, use a simple character similarity check
        if len(word1) > 3 and len(word2) > 3:
            common_chars = set(word1) & set(word2)
            total_chars = set(word1) | set(word2)
            if total_chars:
                similarity = len(common_chars) / len(total_chars)
                return similarity >= 0.6  # 60% character overlap
        
        return False
    
    def get_top_series_page(self, page: int = 1) -> List[Dict]:
        """
        Get top series - the website doesn't seem to have pagination for this,
        but we'll return the same results for any page to maintain consistency
        """
        return self.get_top_series()  # Just return the same result for any page number

    def _calculate_match_score(self, query: str, title: str) -> int:
        """
        Calculate a match score based on how closely the query matches the title
        Higher score means better match
        """
        import re
        
        score = 0
        query_lower = query.lower()
        title_lower = title.lower()
        
        # Clean the strings to remove special characters for comparison
        clean_query = re.sub(r'[^\w\s]', ' ', query_lower).strip()
        clean_title = re.sub(r'[^\w\s]', ' ', title_lower).strip()
        
        # Exact match gets very high score
        if query_lower == title_lower:
            return 1000
        
        # Check if query appears at the beginning of title
        if title_lower.startswith(query_lower):
            score += 200  # High score for beginning match
        
        # Check if query is contained in title
        if query_lower in title_lower:
            score += 150  # High score for substring match
        
        # Check for word-level matches
        query_words = [word for word in clean_query.split() if word]
        title_words = [word for word in clean_title.split() if word]
        
        # For each query word, see how many match title words
        word_matches = 0
        for q_word in query_words:
            for t_word in title_words:
                if q_word == t_word:
                    word_matches += 1
                    break
                elif self._words_approximate_match(q_word, t_word):
                    word_matches += 0.8  # Partial credit for approximate matches
                    break
        
        if query_words:
            # Calculate word match ratio and apply to score
            word_match_ratio = word_matches / len(query_words)
            score += int(word_match_ratio * 100)
        
        # Bonus for matches in the first few words of title
        first_words = ' '.join(title_words[:3]).lower()
        if query_lower in first_words:
            score += 50  # Bonus for appearing early in title
        
        return score
    
    def scrape_any(self, url: str) -> Dict:
        """
        Unified function to automatically detect and scrape film or series
        """
        # Check if it's a film URL based on domain or path patterns
        if 'lk21official.life' in url:
            # This appears to be a film URL
            return self.scrape_film(url)
        elif 'nontondrama.my' in url:
            # Check if it contains episode/season in the path
            if any(keyword in url.lower() for keyword in ['episode', 'eps', 'season']):
                # This is an episode URL, so we should get the series info
                # First, we need to find the series URL from this episode URL
                # For now, we'll scrape this as an episode and return
                return self.scrape_episode(url)
            else:
                # This appears to be a series URL
                return self.scrape_series(url)
        else:
            # Guess based on URL structure
            if any(keyword in url.lower() for keyword in ['episode', 'eps', 'season']):
                return self.scrape_episode(url)
            else:
                # Default to film
                return self.scrape_film(url)

    def scrape_from_user_url(self, url: str) -> Dict:
        """
        Scrape content from any URL provided by the user
        This can handle both direct film/series URLs and episode URLs
        """
        # Normalize the URL by ensuring it has the proper protocol
        if not url.startswith(('http://', 'https://')):
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                # If it's an absolute path, we need to know the base domain
                # For now, return an error since we don't know the domain
                return {
                    'error': 'Invalid URL format. Please include the full URL with protocol (http:// or https://).',
                    'url': url
                }
            else:
                url = 'https://' + url
        
        # Use the existing scrape_any function
        return self.scrape_any(url)


# Example usage
if __name__ == "__main__":
    scraper = StreamingScraper()
    
    # Test film scraping
    print("Testing film scraping...")
    film_data = scraper.scrape_film('https://tv12.lk21official.life/sirat-2025')
    print(json.dumps(film_data, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Test series scraping
    print("Testing series scraping...")
    series_data = scraper.scrape_series('https://tv1.nontondrama.my/alice-in-borderland-2020')
    print(json.dumps(series_data, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Test unified scraping function
    print("Testing unified scraping function...")
    unified_film = scraper.scrape_any('https://tv12.lk21official.life/sirat-2025')
    print(json.dumps(unified_film, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    unified_series = scraper.scrape_any('https://tv1.nontondrama.my/alice-in-borderland-2020')
    print(json.dumps(unified_series, indent=2))
    
    print("\n" + "="*50 + "\n")
    
    # Test getting latest films
    print("Latest films:")
    latest_films = scraper.get_latest_films(1)
    for film in latest_films[:5]:  # Show first 5
        print(f"- {film['title']}: {film['url']}")
    
    print("\n" + "="*50 + "\n")
    
    # Test getting top series
    print("Top series:")
    top_series = scraper.get_top_series()
    for series in top_series[:5]:  # Show first 5
        print(f"- {series['title']}: {series['url']}")
    
    print("\n" + "="*50 + "\n")
    
    # Test search functionality
    print("Searching for 'Alice':")
    search_results = scraper.search('Alice')
    for result in search_results:
        print(f"- {result['type']}: {result['title']}: {result['url']}")