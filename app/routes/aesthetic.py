from flask import Blueprint, request, jsonify, session
from app.services.lm_studio_service import generate_aesthetic_theme
from app.utils.helpers import get_storage

bp = Blueprint('aesthetic', __name__)

@bp.route('/generate_aesthetic_theme', methods=['POST'])
def generate_aesthetic_theme_route():
    session_id = session['id']
    storage = get_storage()
    world_description = storage[session_id].get('world_description', '')
    approved_assets = storage[session_id].get('approved_assets', [])
    
    aesthetic_theme = generate_aesthetic_theme(world_description, approved_assets)
    storage[session_id]['aesthetic_theme'] = aesthetic_theme
    return jsonify({"aesthetic_theme": aesthetic_theme})