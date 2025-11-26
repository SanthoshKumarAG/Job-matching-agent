import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

class JobScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def search_jobs(self, job_title, location, job_type='all'):
        """
        Search jobs from multiple FREE sources
        No API key needed - uses public search
        """
        jobs = []
        
        # Source 1: TheMuseAPI (Free, no auth needed)
        try:
            jobs += self._search_muse(job_title, location)
        except Exception as e:
            print(f"Muse error: {e}")
        
        # Source 2: GitHub Jobs (Free public data)
        try:
            jobs += self._search_github_jobs(job_title, location)
        except Exception as e:
            print(f"GitHub jobs error: {e}")
        
        # Source 3: HN Jobs (Free public data)
        try:
            jobs += self._search_hn_jobs(job_title, location)
        except Exception as e:
            print(f"HN jobs error: {e}")
        
        # Remove duplicates
        seen = set()
        unique_jobs = []
        for job in jobs:
            key = (job.get('title', ''), job.get('company', ''))
            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs[:50]  # Return top 50
    
    def _search_muse(self, job_title, location):
        """The Muse API - Free tier"""
        jobs = []
        url = "https://www.themuse.com/api/public/jobs"
        params = {
            'page': 1,
            'category': job_title,
            'location': location,
            'results_per_page': 10
        }
        try:
            r = requests.get(url, params=params, timeout=10, headers=self.headers)
            if r.status_code == 200:
                data = r.json()
                for job in data.get('results', []):
                    jobs.append({
                        'title': job.get('name', 'N/A'),
                        'company': job.get('company', {}).get('name', 'N/A'),
                        'location': job.get('locations', [{}]).get('name', location) if job.get('locations') else location,
                        'description': job.get('contents', '')[:300],
                        'url': job.get('refs', {}).get('landing_page', ''),
                        'source': 'The Muse',
                        'job_type': job.get('type', 'Full-time'),
                        'posted_date': job.get('publication_date', '').split('T') if job.get('publication_date') else 'N/A',
                        'salary': 'Not specified'
                    })
        except Exception as e:
            print(f"Muse scrape error: {e}")
        return jobs
    
    def _search_github_jobs(self, job_title, location):
        """GitHub Jobs - Free public board"""
        jobs = []
        url = f"https://jobs.github.com/positions.json"
        params = {'description': job_title, 'location': location}
        try:
            r = requests.get(url, params=params, timeout=10, headers=self.headers)
            if r.status_code == 200:
                for job in r.json()[:10]:
                    jobs.append({
                        'title': job.get('title', 'N/A'),
                        'company': job.get('company', 'N/A'),
                        'location': job.get('location', location),
                        'description': BeautifulSoup(job.get('description', ''), 'html.parser').get_text()[:300],
                        'url': job.get('url', ''),
                        'source': 'GitHub Jobs',
                        'job_type': 'Full-time',
                        'posted_date': job.get('created_at', '').split('T') if job.get('created_at') else 'N/A',
                        'salary': 'Not specified'
                    })
        except Exception as e:
            print(f"GitHub jobs error: {e}")
        return jobs
    
    def _search_hn_jobs(self, job_title, location):
        """Hacker News Jobs - Free public board"""
        jobs = []
        try:
            url = "https://news.ycombinator.com/jobs"
            r = requests.get(url, timeout=10, headers=self.headers)
            if r.status_code == 200:
                soup = BeautifulSoup(r.content, 'html.parser')
                rows = soup.find_all('tr', {'class': 'athing'})
                for row in rows[:5]:
                    title_elem = row.find('span', {'class': 'titleline'})
                    if title_elem:
                        title = title_elem.get_text()
                        if job_title.lower() in title.lower() or 'finance' in title.lower() or 'data' in title.lower():
                            jobs.append({
                                'title': title,
                                'company': location,
                                'location': location,
                                'description': title[:300],
                                'url': 'https://news.ycombinator.com/jobs',
                                'source': 'HN Jobs',
                                'job_type': 'Full-time',
                                'posted_date': 'N/A',
                                'salary': 'Not specified'
                            })
        except Exception as e:
            print(f"HN jobs error: {e}")
        return jobs
