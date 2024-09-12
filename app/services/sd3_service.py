import requests
from config import SD_URL

def get_available_samplers():
    try:
        response = requests.get(f"{SD_URL}/sdapi/v1/samplers")
        response.raise_for_status()
        return [sampler['name'] for sampler in response.json()]
    except Exception as e:
        print(f"Failed to fetch available samplers: {str(e)}")
        return ["Euler"]  # Default to Euler if we can't fetch the list

available_samplers = get_available_samplers()
preferred_sampler = "DPM++ SDE Karras" if "DPM++ SDE Karras" in available_samplers else "Euler"

def generate_images(approved_prompts):
    generated_images = []

    print(f"Generating images for {len(approved_prompts)} prompts")

    for prompt_data in approved_prompts:
        asset = prompt_data['asset']
        prompt = prompt_data['prompt']

        print(f"Generating image for asset: {asset['name']}")

        sd_params = {
            "prompt": prompt['prompt'],
            "negative_prompt": ", ".join(prompt["negative_prompt"]) if isinstance(prompt["negative_prompt"], list) else prompt["negative_prompt"],
            "steps": 20,
            "width": 1024,
            "height": 1024,
            "tiling": asset['type'] == 'tile'  # Set tiling to True for tile assets, False otherwise
        }

        print(f"SD3 params: {sd_params}")

        try:
            response = requests.post(
                f"{SD_URL}/sdapi/v1/txt2img",
                json=sd_params
            )
            print(f"SD3 API response status: {response.status_code}")
            
            if response.status_code == 200:
                image_data = response.json()['images'][0]
                generated_images.append({
                    "asset": asset,
                    "image": image_data
                })
            else:
                print(f"SD3 API error response: {response.text}")
                raise Exception(f"Failed to generate image for {asset['name']}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request error: {str(e)}")
            raise

    return generated_images

def regenerate_image(prompt_data):
    asset = prompt_data['asset']
    prompt = prompt_data['prompt']

    sd_params = {
        "prompt": prompt['prompt'],
        "negative_prompt": prompt["negative_prompt"],
        "steps": 20,
        "width": 1024,
        "height": 1024,
        "tiling": asset['type'] == 'tile'  # Set tiling to True for tile assets, False otherwise
    }

    response = requests.post(
        f"{SD_URL}/sdapi/v1/txt2img",
        json=sd_params
    )

    if response.status_code == 200:
        image_data = response.json()['images'][0]
        return image_data
    else:
        raise Exception(f"Failed to regenerate image for {asset['name']}. Status code: {response.status_code}")