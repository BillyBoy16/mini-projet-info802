from flask import Flask, render_template
from config import Config
from extensions import db, jwt
from flask_cors import CORS

def create_app():
 app = Flask(__name__)
 app.config.from_object(Config)
 #initialise les extensions
 CORS(app)
 db.init_app(app)
 jwt.init_app(app)
 @app.route('/')
 def index():
   return render_template('index.html')
 #importe les routes
 from routes.trajet_routes import trajet_bp
 app.register_blueprint(trajet_bp, url_prefix="/api")
 from routes.borne_routes import borne_bp
 app.register_blueprint(borne_bp, url_prefix="/api")

 with app.app_context():
    db.create_all()
 return app

app = create_app()

if __name__ == "__main__":
 app.run(debug=True)