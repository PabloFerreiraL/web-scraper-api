from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import logging, json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from datetime import timedelta
from dotenv import load_dotenv

from app.scraper import WebScraper
from app.site_navigator import SiteNavigator
from app.cache_manager import CacheManager
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# JWT Configuration
jwt_secret_key = os.getenv('JWT_SECRET_KEY')
if not jwt_secret_key:
    raise ValueError("JWT_SECRET_KEY must be set in .env file")

app.config['JWT_SECRET_KEY'] = jwt_secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
jwt = JWTManager(app)

# Rate Limiter Configuration
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize cache manager
cache = CacheManager()

@app.route('/login', methods=['POST'])
def login():
    try:
        username = request.json.get('username')
        password = request.json.get('password')

        print(f"Username: {username}, Password: {password}")
        
        if not username or not password:
            return jsonify({'error': 'Missing credentials'}), 400
            
        if username == "admin" and password == "password":
            access_token = create_access_token(identity=username)
            return jsonify({'access_token': access_token}), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scrape', methods=['POST'])
@jwt_required()
def scrape():
    try:
        url = request.json.get('url')
        params = request.json.get('params', [])

        if not url:
            return jsonify({'error': 'URL is required'}), 400

        # Check cache before scraping  
        cached_result = cache.get(url)
        if cached_result:
            return jsonify({
                'data': cached_result,
                'source': 'cache'
            }), 200
            
        # Scraping
        scraper = WebScraper()
        result = scraper.scrape(url, params)
        
        # Cache the result
        cache.set(url, result)
        
        return jsonify({
            'data': result,
            'source': 'fresh'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/scrape/site', methods=['POST'])
@jwt_required()
#@limiter.limit("2 per hour")
def scrape_site():
    try:
        url = request.json.get('url')
        max_pages = request.json.get('max_pages', 10)
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
            
        navigator = SiteNavigator()
        results = navigator.crawl(url, max_pages)
        
        return jsonify({
            'data': results,
            'pages_crawled': len(results)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)