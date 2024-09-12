import requests
import json
import re
import time
from flask import jsonify
from config import LM_STUDIO_URL

def generate_game_world(description):
    system_prompt = """
    You are a creative game designer. Given a game world description, generate a list of key items, game assets, and interactive entities that would populate this world. Include at least one of each type: location, item, interactive entity, and tile. Include around 20 assets in total.

    For tiles, provide a description of a repeatable background element that can be used to create larger game environments. Tiles can represent terrain (e.g., grass, water, sand), architectural elements (e.g., wall sections, floor patterns), or environmental details (e.g., foliage, rocks).

    Interactive entities can include AI-controlled elements (e.g., enemies, NPCs), player-controlled elements (e.g., characters, vehicles, ships), or any other dynamic, interactive object in the game world. We must include one player controlled elements.

    Locations can include a description of a 2D video game scene with depth and a sense of scale. This can be a city, a dungeon, a battlefield, or anything else that makes sense for the game.

    Respond ONLY with a JSON array of objects, each with 'name' and 'type' (location/item/interactive_entity/tile) properties. Do not include any explanatory text or code blocks.
    """

    try:
        response = requests.post(
            f"{LM_STUDIO_URL}/v1/chat/completions",
            json={
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": description}
                ],
                "temperature": 0.7,
                "max_tokens": -1
            },
            timeout=120
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # Try to extract JSON from the content
        try:
            game_world = json.loads(content)
        except json.JSONDecodeError:
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            if json_start != -1 and json_end != -1:
                json_content = content[json_start:json_end]
                game_world = json.loads(json_content)
            else:
                raise ValueError(f"Unable to parse JSON from content: {content}")
        
        if not isinstance(game_world, list):
            raise ValueError(f"Expected a list, but got: {type(game_world)}")
        
        return game_world
    except Exception as e:
        raise Exception(f"Error generating game world: {str(e)}")

def generate_aesthetic_theme(world_description, approved_assets):
    system_prompt = """
    You are an expert game art director. Given a game world description and a list of approved assets, create a cohesive aesthetic theme that will guide the visual style of all game assets. 

    Provide a concise description of the aesthetic theme in the following format:

    AESTHETIC_THEME_START
    Art Style: [Overall art style in 5-10 words]
    Color Palette: [Main colors and their relationships in 10-15 words]
    Lighting: [Lighting style and mood in 5-10 words]
    Key Elements: [3-5 recurring visual motifs or elements, comma-separated]
    Atmosphere: [Overall mood or atmosphere in 5-10 words]
    AESTHETIC_THEME_END

    Ensure your response fits within the delimiters and provides specific, consistent descriptions for a unified look across all assets.
    """

    try:
        response = requests.post(
            f"{LM_STUDIO_URL}/v1/chat/completions",
            json={
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"World Description: {world_description}\nApproved Assets: {json.dumps(approved_assets)}"}
                ],
                "temperature": 0.7,
                "max_tokens": 400
            },
            timeout=120
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        
        # Extract the aesthetic theme from between the delimiters
        start_delimiter = "AESTHETIC_THEME_START"
        end_delimiter = "AESTHETIC_THEME_END"
        start_index = content.find(start_delimiter)
        end_index = content.find(end_delimiter)
        
        if start_index != -1 and end_index != -1:
            aesthetic_theme = content[start_index + len(start_delimiter):end_index].strip()
            return aesthetic_theme
        else:
            raise ValueError("Aesthetic theme not found in the expected format")
    except Exception as e:
        raise Exception(f"Error generating aesthetic theme: {str(e)}")

def generate_image_prompts(approved_assets, world_description, aesthetic_theme):
    system_prompt = """
    You are an expert in creating concise image prompts for 2D pixel art game assets. Your task is to create brief prompts that will guide an AI image generator to create suitable pixel art representations for game assets.

    Key instructions:
    1. Always include the terms "pixelart", "pixel art", or "sprite" in the prompt.
    2. Keep the prompt extremely concise, ideally around 15-20 words maximum.
    3. Focus only on the most essential visual elements and characteristics of the asset.
    4. Use simple, clear language that describes the asset's key features and unique characteristics.
    5. Incorporate only the most relevant elements from the provided aesthetic theme.
    6. For locations, describe a detailed 2D video game scene with depth.
    7. For items and characters, include "centered on pure white background, studio lighting, product photography style, isolated, full object visible".
    8. For tiles, describe a seamless, repeatable background element following the tiling guide.
    9. For characters and items, specify the view (e.g., "front view", "3/4 view", "isometric view").

    Respond with a JSON object containing only the following keys:
    - "prompt": A brief description of the asset, including the pixel art terms and specific instructions based on asset type.
    - "negative_prompt": A short list of elements to exclude, focusing on maintaining a clean, pixel art style.

    Do not include any explanatory text or code blocks in your response.
    """

    image_prompts = []
    
    for asset in approved_assets:
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                asset_specific_prompt = f"Create an image prompt for this {asset['type']} game asset: {asset['name']}"
                
                response = requests.post(
                    f"{LM_STUDIO_URL}/v1/chat/completions",
                    json={
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"World Context: {world_description}\nAesthetic Theme: {aesthetic_theme}\n{asset_specific_prompt}"}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 150
                    },
                    timeout=120
                )
                response.raise_for_status()
                content = response.json()['choices'][0]['message']['content']
                
                # Try to parse the JSON content
                try:
                    prompt = json.loads(content)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract JSON from the content
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        prompt = json.loads(json_match.group())
                    else:
                        raise ValueError(f"Unable to extract valid JSON from content: {content}")
                
                if not isinstance(prompt, dict) or 'prompt' not in prompt or 'negative_prompt' not in prompt:
                    raise ValueError(f"Invalid prompt structure: {prompt}")
                
                image_prompts.append({"asset": asset, "prompt": prompt})
                break  # Success, exit retry loop
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Error generating prompt for {asset['name']} (Attempt {attempt + 1}): {str(e)}")
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise Exception(f"Failed to generate prompt for {asset['name']} after {max_retries} attempts. Error: {str(e)}")

    return image_prompts