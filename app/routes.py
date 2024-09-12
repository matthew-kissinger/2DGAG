from flask import render_template, request, jsonify, session, send_file
from app import app
import json
from config import SD_URL
import time
import io
import zipfile
import base64
import uuid
import requests
from app.services.lm_studio_service import generate_game_world, generate_aesthetic_theme, generate_image_prompts

# In-memory storage (replace with a database in production)
storage = {}

@app.route('/')
def index():
    session['id'] = str(uuid.uuid4())
    return render_template('index.html')

# ... rest of the code remains the same ...