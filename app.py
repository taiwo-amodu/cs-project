from flask import Flask

from flask_cors import CORS
from api.services import services_bp
from api.reviews import reviews_bp
from api.routing import routing_bp
from flask import Flask, render_template

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(services_bp)
app.register_blueprint(reviews_bp)
app.register_blueprint(routing_bp)

@app.route('/')
def index():
    return render_template('map.html')

if __name__ == '__main__':
    app.run(debug=True)
