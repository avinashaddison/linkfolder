import os
import logging
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from link_extractor import LinkExtractor

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Initialize link extractor
link_extractor = LinkExtractor()

@app.route('/')
def index():
    """Main page with URL input form"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search_movies():
    """Search for movies on MoviesDrive.cc"""
    keyword = request.form.get('keyword', '').strip()
    
    if not keyword:
        flash('Please enter a movie name to search', 'error')
        return redirect(url_for('index'))
    
    try:
        # Search for movies
        result = link_extractor.search_movies(keyword)
        
        if result['error']:
            flash(result['error'], 'error')
            return redirect(url_for('index'))
        
        if not result['movies']:
            flash(f'No movies found for "{keyword}"', 'error')
            return redirect(url_for('index'))
        
        return render_template('search_results.html', 
                             keyword=keyword,
                             movies=result['movies'],
                             total_count=result['total_count'])
    
    except Exception as e:
        logging.error(f"Error searching movies: {str(e)}")
        flash('An unexpected error occurred while searching', 'error')
        return redirect(url_for('index'))

@app.route('/extract', methods=['POST'])
def extract_links():
    """Extract links from the provided URL"""
    url = request.form.get('url', '').strip()
    
    if not url:
        flash('Please enter a valid URL', 'error')
        return redirect(url_for('index'))
    
    try:
        # Extract links from the URL
        result = link_extractor.extract_links(url)
        
        if result['error']:
            flash(result['error'], 'error')
            return redirect(url_for('index'))
        
        return render_template('results.html', 
                             url=url,
                             links=result['links'],
                             categories=result['categories'],
                             total_count=result['total_count'])
    
    except Exception as e:
        logging.error(f"Error extracting links: {str(e)}")
        flash('An unexpected error occurred while extracting links', 'error')
        return redirect(url_for('index'))

@app.route('/api/extract', methods=['POST'])
def api_extract_links():
    """API endpoint for extracting links (for AJAX requests)"""
    data = request.get_json()
    url = data.get('url', '').strip() if data else ''
    
    if not url:
        return jsonify({'error': 'Please provide a valid URL'}), 400
    
    try:
        result = link_extractor.extract_links(url)
        return jsonify(result)
    
    except Exception as e:
        logging.error(f"API error extracting links: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred while extracting links'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
