from flask import Blueprint, request, jsonify, session
from app.services.lm_studio_service import generate_game_world
from app.utils.helpers import get_storage
import uuid  # Add this import

bp = Blueprint('game_world', __name__)

@bp.route('/generate_game_world', methods=['POST'])
def generate_game_world_route():
    description = request.json.get('description')
    if 'id' not in session:
        session['id'] = str(uuid.uuid4())
    session_id = session['id']
    storage = get_storage()
    storage[session_id] = {'world_description': description}
    
    game_world = generate_game_world(description)
    storage[session_id]['game_world'] = game_world
    return jsonify(game_world)

@bp.route('/approve_asset_list', methods=['POST'])
def approve_asset_list():
    approved_assets = request.json.get('approved_assets')
    custom_assets = request.json.get('custom_assets', [])
    if 'id' not in session:
        session['id'] = str(uuid.uuid4())
    session_id = session['id']
    storage = get_storage()
    storage[session_id]['approved_assets'] = approved_assets + custom_assets
    return jsonify({"message": "Asset list approved", "approved_assets": storage[session_id]['approved_assets']})