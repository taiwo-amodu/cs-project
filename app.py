import os
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv  # Ensure environment variables are loaded

# Import blueprints
from api.services import services_bp
from api.reviews import reviews_bp
from api.routing import routing_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(services_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(routing_bp)

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/api/google-maps-key', methods=['GET'])
def get_google_maps_key():
    """Securely returns the Google Maps API key."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        return jsonify({"error": "API key not found"}), 500
    return jsonify({"api_key": api_key})

if __name__ == '__main__':
    app.run(debug=True)
