from flask import Flask
from blueprints.auth import auth_bp
from blueprints.home import home_bp
from blueprints.about_us import aboutus_bp

app = Flask(__name__)
app.secret_key = "chiavesessione"

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(aboutus_bp)

if __name__ == "__main__":
    app.run(debug = True, port=5001)