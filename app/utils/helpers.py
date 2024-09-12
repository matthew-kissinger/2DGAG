import io
import json
import zipfile
import base64

storage = {}

def get_storage():
    return storage

def create_game_zip(game_data):
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        zf.writestr('game_data.json', json.dumps(game_data, indent=2))
        for image_data in game_data.get('generated_images', []):
            asset_name = image_data['asset']['name']
            safe_filename = ''.join(c if c.isalnum() or c in ['-', '_'] else '_' for c in asset_name)
            zf.writestr(f'{safe_filename}.png', base64.b64decode(image_data['image']))
    memory_file.seek(0)
    return memory_file