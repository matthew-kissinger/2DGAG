from flask import Flask, render_template, request, jsonify, session, send_file
import json
from config import SD_URL
import time
import io
import zipfile
import base64
import uuid
from services.lm_studio_service import generate_game_world, generate_aesthetic_theme, generate_image_prompts

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure random key

# In-memory storage (replace with a database in production)
storage = {}

@app.route('/')
def index():
    session['id'] = str(uuid.uuid4())
    return render_template('index.html')

@app.route('/generate_game_world', methods=['POST'])
def generate_game_world_route():
    description = request.json.get('description')
    session_id = session['id']
    storage[session_id] = {'world_description': description}
    
    try:
        game_world = generate_game_world(description)
        storage[session_id]['game_world'] = game_world
        return jsonify(game_world)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/approve_asset_list', methods=['POST'])
def approve_asset_list():
    approved_assets = request.json.get('approved_assets')
    custom_assets = request.json.get('custom_assets', [])
    session_id = session['id']
    storage[session_id]['approved_assets'] = approved_assets + custom_assets
    return jsonify({"message": "Asset list approved", "approved_assets": storage[session_id]['approved_assets']})

@app.route('/generate_aesthetic_theme', methods=['POST'])
def generate_aesthetic_theme_route():
    session_id = session['id']
    world_description = storage[session_id].get('world_description', '')
    approved_assets = storage[session_id].get('approved_assets', [])
    
    try:
        aesthetic_theme = generate_aesthetic_theme(world_description, approved_assets)
        storage[session_id]['aesthetic_theme'] = aesthetic_theme
        return jsonify({"aesthetic_theme": aesthetic_theme})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_image_prompts', methods=['POST'])
def generate_image_prompts_route():
    session_id = session['id']
    approved_assets = storage[session_id].get('approved_assets', [])
    world_description = storage[session_id].get('world_description', '')
    aesthetic_theme = storage[session_id].get('aesthetic_theme', '')

    if not approved_assets:
        return jsonify({"error": "No approved assets found. Please generate and approve assets first."}), 400

    if not aesthetic_theme:
        return jsonify({"error": "No aesthetic theme found. Please generate an aesthetic theme first."}), 400

    try:
        image_prompts = generate_image_prompts(approved_assets, world_description, aesthetic_theme)
        return jsonify(image_prompts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/approve_image_prompts', methods=['POST'])
def approve_image_prompts():
    approved_prompts = request.json.get('approved_prompts')
    session_id = session['id']
    storage[session_id]['approved_prompts'] = approved_prompts
    return jsonify({"message": "Image prompts approved"})

@app.route('/generate_images', methods=['POST'])
def generate_images():
    session_id = session['id']
    approved_prompts = storage[session_id].get('approved_prompts', [])
    generated_images = []

    for prompt_data in approved_prompts:
        asset = prompt_data['asset']
        prompt = prompt_data['prompt']

        # Add default values
        sd_params = {
            "prompt": prompt["prompt"],
            "negative_prompt": prompt["negative_prompt"],
            "steps": 20,
            "width": 1024,
            "height": 1024,
            "sampler_name": "Euler"
        }

        # SD3 API call
        response = requests.post(
            f"{SD_URL}/sdapi/v1/txt2img",
            json=sd_params
        )

        if response.status_code == 200:
            image_data = response.json()['images'][0]
            generated_images.append({
                "asset": asset,
                "image": image_data
            })
        else:
            return jsonify({"error": f"Failed to generate image for {asset['name']}"}), 500

    storage[session_id]['generated_images'] = generated_images
    return jsonify(generated_images)

@app.route('/regenerate_image', methods=['POST'])
def regenerate_image():
    session_id = session['id']
    index = request.json.get('index')
    approved_prompts = storage[session_id].get('approved_prompts', [])
    
    if index < 0 or index >= len(approved_prompts):
        return jsonify({"error": "Invalid index"}), 400

    prompt_data = approved_prompts[index]
    asset = prompt_data['asset']
    prompt = prompt_data['prompt']

    sd_params = {
        "prompt": prompt["prompt"],
        "negative_prompt": prompt["negative_prompt"],
        "steps": 20,
        "width": 1024,
        "height": 1024,
        "sampler_name": "Euler"
    }

    response = requests.post(
        f"{SD_URL}/sdapi/v1/txt2img",
        json=sd_params
    )

    if response.status_code == 200:
        image_data = response.json()['images'][0]
        storage[session_id]['generated_images'][index]['image'] = image_data
        return jsonify({"image": image_data})
    else:
        return jsonify({"error": f"Failed to regenerate image for {asset['name']}"}), 500

@app.route('/save_game', methods=['POST'])
def save_game():
    session_id = session['id']
    game_data = storage[session_id]

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        zf.writestr('game_data.json', json.dumps(game_data, indent=2))
        for image_data in game_data.get('generated_images', []):
            asset_name = image_data['asset']['name']
            # Replace spaces with underscores and remove any non-alphanumeric characters
            safe_filename = ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in asset_name)
            zf.writestr(f'{safe_filename}.png', base64.b64decode(image_data['image']))

    memory_file.seek(0)
    return send_file(memory_file, 
                     download_name='game_world.zip', 
                     as_attachment=True,
                     mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True)