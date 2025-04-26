from flask import Flask, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt

from services.models import db, User
from blueprints.auth import auth_bp
from blueprints.home import home_bp
from blueprints.playlist import playlist_bp
from blueprints.spotify import spotify_bp
from blueprints.compare import compare_bp
from blueprints.suggested import suggested_bp

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spotipy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "chiavesessione"

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(playlist_bp)
app.register_blueprint(spotify_bp)
app.register_blueprint(suggested_bp)
app.register_blueprint(compare_bp, url_prefix='/compare')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

if __name__ == "__main__":
    app.run(debug = True, port=5004)

