from flask import Flask, render_template, send_from_directory, session
from config import Config
import os
import secrets
import uuid

def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='/static')
    app.config.from_object(Config)
    
    # Generate a random secret key
    app.secret_key = secrets.token_hex(16)

    from app.routes import game_world, aesthetic, image_prompts, images
    app.register_blueprint(game_world.bp)
    app.register_blueprint(aesthetic.bp)
    app.register_blueprint(image_prompts.bp)
    app.register_blueprint(images.bp)

    @app.route('/')
    def index():
        if 'id' not in session:
            session['id'] = str(uuid.uuid4())
        return render_template('index.html')

    return app