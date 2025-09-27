import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, List, Optional


class StreamingScraper:
    def __init__(self):
        self.session = requests.Session()
        # Set a user agent to avoid being blocked
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def scrape_film(self, film_url: str) -> Dict:
        """
        Scrape information from a film page
        Returns: Dictionary with film title and embedded player links
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
                'players': player_links
            }
        except Exception as e:
            print(f"Error scraping film {film_url}: {str(e)}")
            return {
                'type': 'film',
                'title': '',
                'url': film_url,
                'players': {},
                'error': str(e)
            }
    
    def scrape_series(self, series_url: str) -> Dict:
        """
        Scrape information from a series page
        Returns: Dictionary with series title, seasons, episodes, and embedded player links
        """
        try:
            response = self.session.get(series_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract series title
            title = soup.title.string if soup.title else ""
            if "|" in title:
                title = title.split("|")[0].strip()
            
            # Find episode links
            episode_links = soup.find_all('a', href=lambda x: x and ('episode' in x.lower() or 'eps' in x.lower()))
            
            episodes_data = {}
            episode_urls = set()
            
            # Extract episode URLs from available links
            for link in episode_links:
                link_text = link.get_text().strip()
                href = link['href']
                
                # Check if this is an episode link
                if 'episode' in href.lower() or 'eps' in href.lower():
                    episode_urls.add((link_text, href))
            
            # For each episode, scrape its player information
            for episode_text, episode_url in episode_urls:
                if episode_url.startswith('/'):
                    episode_url = 'https://tv1.nontondrama.my' + episode_url
                
                episode_detail = self.scrape_episode(episode_url)
                
                # Extract season and episode number from the URL or text
                season_episode_info = self._extract_season_episode(episode_text, episode_url)
                
                if season_episode_info:
                    season_num = season_episode_info.get('season', 'unknown')
                    episode_num = season_episode_info.get('episode', 'unknown')
                    
                    season_key = f'Season {season_num}'
                    episode_key = f'Episode {episode_num}'
                    
                    if season_key not in episodes_data:
                        episodes_data[season_key] = {}
                    
                    episodes_data[season_key][episode_key] = episode_detail
            
            return {
                'type': 'series',
                'title': title,
                'url': series_url,
                'episodes': episodes_data
            }
        except Exception as e:
            print(f"Error scraping series {series_url}: {str(e)}")
            return {
                'type': 'series',
                'title': '',
                'url': series_url,
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
        Get list of latest films from the main page
        """
        try:
            film_url = f'https://tv12.lk21official.life/latest/page/{page}'
            response = self.session.get(film_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find film links
            film_elements = soup.find_all('article')
            films = []
            
            for item in film_elements:
                link = item.find('a', href=True)
                if link:
                    relative_url = link['href']
                    if not relative_url.startswith('http'):
                        relative_url = 'https://tv12.lk21official.life' + relative_url
                    
                    films.append({
                        'title': link.get_text().strip(),
                        'url': relative_url
                    })
            
            return films
        except Exception as e:
            print(f"Error getting latest films: {str(e)}")
            return []
    
    def get_top_series(self) -> List[Dict]:
        """
        Get list of top series from the main series page
        """
        try:
            series_url = 'https://tv1.nontondrama.my/top-series-today'
            response = self.session.get(series_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find series links
            series_elements = soup.find_all('article')
            series_list = []
            
            for item in series_elements:
                link = item.find('a', href=True)
                if link:
                    relative_url = link['href']
                    if not relative_url.startswith('http'):
                        relative_url = 'https://tv1.nontondrama.my' + relative_url
                    
                    series_list.append({
                        'title': link.get_text().strip(),
                        'url': relative_url
                    })
            
            return series_list
        except Exception as e:
            print(f"Error getting top series: {str(e)}")
            return []
    
    # Updated search functionality with better implementation
    def search(self, query: str, media_type: str = 'all') -> List[Dict]:
        """
        Search functionality that checks multiple pages for better results
        """
        results = []
        query_lower = query.lower()
        
        # Search films
        if media_type in ['all', 'film']:
            # Check first few pages for films
            for page in range(1, 3):  # Check first 2 pages
                latest_films = self.get_latest_films(page)
                for film in latest_films:
                    if query_lower in film['title'].lower():
                        results.append({
                            'type': 'film',
                            'title': film['title'],
                            'url': film['url']
                        })
        
        # Search series
        if media_type in ['all', 'series']:
            # Check the top series page
            top_series = self.get_top_series()
            for series in top_series:
                if query_lower in series['title'].lower():
                    results.append({
                        'type': 'series',
                        'title': series['title'],
                        'url': series['url']
                    })
        
        return results

# Main function to demonstrate usage
def main():
    scraper = StreamingScraper()
    
    print("Streaming Site Scraper")
    print("="*50)
    
    while True:
        print("\nOptions:")
        print("1. Scrape a film")
        print("2. Scrape a series")
        print("3. Get latest films")
        print("4. Get top series")
        print("5. Search")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            url = input("Enter film URL: ").strip()
            if url:
                print(f"\nScraping film: {url}")
                result = scraper.scrape_film(url)
                print(json.dumps(result, indent=2))
        
        elif choice == '2':
            url = input("Enter series URL: ").strip()
            if url:
                print(f"\nScraping series: {url}")
                result = scraper.scrape_series(url)
                print(json.dumps(result, indent=2))
        
        elif choice == '3':
            print(f"\nGetting latest films...")
            results = scraper.get_latest_films(1)
            for i, film in enumerate(results[:10], 1):  # Show first 10
                print(f"{i}. {film['title']}: {film['url']}")
        
        elif choice == '4':
            print(f"\nGetting top series...")
            results = scraper.get_top_series()
            for i, series in enumerate(results[:10], 1):  # Show first 10
                print(f"{i}. {series['title']}: {series['url']}")
        
        elif choice == '5':
            query = input("Enter search query: ").strip()
            if query:
                print(f"\nSearching for: {query}")
                results = scraper.search(query)
                if results:
                    for i, result in enumerate(results, 1):
                        print(f"{i}. [{result['type']}] {result['title']}: {result['url']}")
                else:
                    print("No results found.")
        
        elif choice == '6':
            print("Exiting...")
            break
        
        else:
            print("Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()