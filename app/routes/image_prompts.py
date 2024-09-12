from flask import Blueprint, request, jsonify, session
from app.services.lm_studio_service import generate_image_prompts
from app.utils.helpers import get_storage

bp = Blueprint('image_prompts', __name__)

@bp.route('/generate_image_prompts', methods=['POST'])
def generate_image_prompts_route():
    session_id = session['id']
    storage = get_storage()
    approved_assets = storage[session_id].get('approved_assets', [])
    world_description = storage[session_id].get('world_description', '')
    aesthetic_theme = storage[session_id].get('aesthetic_theme', '')
    
    result = generate_image_prompts(approved_assets, world_description, aesthetic_theme)
    
    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], dict) and 'error' in result[0]:
        return jsonify(result[0]), result[1]
    
    return jsonify(result)

@bp.route('/approve_image_prompts', methods=['POST'])
def approve_image_prompts():
    approved_prompts = request.json.get('approved_prompts')
    session_id = session['id']
    storage = get_storage()
    storage[session_id]['approved_prompts'] = approved_prompts
    return jsonify({"message": "Image prompts approved"})