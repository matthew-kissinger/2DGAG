# 2D Game Asset Generator

Create game 2d game assets locally with AI. Leverage your unused computer power to generate assets for your games.

## What's this?

World Creation Engine is a tool that leverages AI to generate game assets. It runs on your local machine, and has been tested using LM Studio with Llama 3.1 8B for chat completions and Automatic1111's Stable Diffusion Web UI for image creation using superPixelartXLMV1_v10 checkpoint (Based model SD XL) which can be found at https://civitai.com/models/581162/superpixelartxlmv1

## Features

- Game world concept generation
- Asset list creation
- Aesthetic theme development
- Image prompt generation
- Asset image creation

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up LM Studio with Llama 3.1 8B model
4. Launch Automatic1111 Stable Diffusion Web UI with the `--api` flag
5. Configure LM Studio and SD Web UI URLs in `config.py`
6. Run the app: `python run.py`
7. Visit `http://localhost:5000` and start creating

## Requirements

- LM Studio running Llama 3.1 8B
- Automatic1111 Stable Diffusion Web UI (launched with `--api` flag)
- Python 3.10+

## Note

This is a work in progress. It might not replace your entire art team yet, but we're getting there.

## Contributing

Got ideas? Found a bug? Contributions are welcome. Open an issue or submit a PR.

## License

MIT - See LICENSE file for details. Use responsibly, we're not responsible for any accidental skynet situations.
