from flask import Flask, render_template, request, jsonify
from job_scraper import JobScraper
from matcher import JobMatcher
import json

app = Flask(__name__, static_folder='public', static_url_path='')

scraper = JobScraper()
matcher = JobMatcher()

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/search-jobs', methods=['POST'])
def search_jobs():
    """
    API endpoint to search and match jobs
    Receives: resume, job_titles, locations, experience, job_type
    Returns: matched jobs sorted by score
    """
    try:
        data = request.json
        resume = data.get('resume', '')
        job_titles = data.get('job_titles', [])
        locations = data.get('locations', [])
        experience = data.get('experience', '2')
        job_type = data.get('job_type', 'all')
        
        if not resume or not job_titles or not locations:
            return jsonify({'error': 'Missing required fields'}), 400
        
        all_jobs = []
        
        # Search jobs from each title/location combination
        for title in job_titles:
            for location in locations:
                try:
                    jobs = scraper.search_jobs(title, location, job_type)
                    all_jobs.extend(jobs)
                except Exception as e:
                    print(f"Error searching {title} in {location}: {e}")
        
        if not all_jobs:
            return jsonify({'jobs': [], 'message': 'No jobs found. Try different search criteria.'})
        
        # Match jobs with resume
        for job in all_jobs:
            match_data = matcher.calculate_match_score(resume, job, experience)
            job['match_score'] = match_data['score']
            job['matched_skills'] = match_data['matched_skills']
        
        # Sort by match score
        all_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return jsonify({'jobs': all_jobs[:30]})  # Return top 30
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
