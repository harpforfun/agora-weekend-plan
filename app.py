from flask import Flask, render_template, request, jsonify
from scraper import search_activities
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def index():
    """Render the main search page"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Handle search requests and return activity results"""
    try:
        # Get search parameters from the request
        query = request.form.get('query', '').strip()
        date = request.form.get('date', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Please enter a search query'
            }), 400
        
        logger.info(f"Searching for: {query}, date: {date}")
        
        # Perform the search
        activities = search_activities(query, date)
        
        return jsonify({
            'success': True,
            'activities': activities,
            'count': len(activities)
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'An error occurred while searching. Please try again.'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal error: {str(error)}")
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
