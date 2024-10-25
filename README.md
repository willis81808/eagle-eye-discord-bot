<div align="center">
    <img wdith="100px", src="https://raw.githubusercontent.com/willis81808/eagle-eye-discord-bot/refs/heads/main/icon.png" />
</div>

# Requirements
- Python ^3.11
- Poetry

# Configuration

## Environment variables
- Copy `.example.env`
- Rename the file to `.env`
- Replace the placeholders with your own OpenAI API key and Discord Bot token

## Application configuration
- Copy `example.config.json`
- Rename the file to `config.json`
- Optionally add your guild ID -> channel ID mappings

# Running locally
- Execute `poetry install` in the project root to create a virtual environment and install the dependencies
- Execute `python main.py` to start the bot