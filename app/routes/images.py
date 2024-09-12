from flask import Blueprint, request, jsonify, session, send_file
from app.services.sd3_service import generate_images, regenerate_image
from app.utils.helpers import get_storage, create_game_zip

bp = Blueprint('images', __name__)

@bp.route('/generate_images', methods=['POST'])
def generate_images_route():
    session_id = session['id']
    storage = get_storage()
    approved_prompts = storage[session_id].get('approved_prompts', [])
    
    print(f"Session ID: {session_id}")
    print(f"Approved prompts: {approved_prompts}")
    
    try:
        generated_images = generate_images(approved_prompts)
        storage[session_id]['generated_images'] = generated_images
        return jsonify(generated_images)
    except Exception as e:
        print(f"Error in generate_images_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/regenerate_image', methods=['POST'])
def regenerate_image_route():
    session_id = session['id']
    index = request.json.get('index')
    storage = get_storage()
    approved_prompts = storage[session_id].get('approved_prompts', [])
    
    if index < 0 or index >= len(approved_prompts):
        return jsonify({"error": "Invalid index"}), 400

    try:
        new_image = regenerate_image(approved_prompts[index])
        storage[session_id]['generated_images'][index]['image'] = new_image
        return jsonify({"image": new_image})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/save_game', methods=['POST'])
def save_game():
    session_id = session['id']
    storage = get_storage()
    game_data = storage[session_id]
    
    memory_file = create_game_zip(game_data)
    return send_file(memory_file, 
                     download_name='game_world.zip', 
                     as_attachment=True,
                     mimetype='application/zip')