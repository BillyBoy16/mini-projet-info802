from flask import Flask, render_template
from config import Config
from flask_cors import CORS

def create_app():
 app = Flask(__name__)
 app.config.from_object(Config)
 CORS(app)
 @app.route('/')
 def index():
   return render_template('index.html')
 #importation les routes
 from routes.trajet_routes import trajet_bp
 app.register_blueprint(trajet_bp, url_prefix="/api")
 from routes.borne_routes import borne_bp
 app.register_blueprint(borne_bp, url_prefix="/api")
 return app

app = create_app()

if __name__ == "__main__":
 app.run(debug=True, port=5000)