# Goose AI Agent Setup with Flox

## Prerequisites
- Flox package manager installed
- API keys for at least one provider (Anthropic recommended)

## Quick Start

1. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your API keys
   nano .env
   ```

2. **Activate the Flox environment**
   ```bash
   # Source your .env file
   source .env
   
   # Activate Flox environment
   flox activate
   ```

3. **Run Goose**
   ```bash
   # Start a Goose session
   goose session
   
   # Or run a single command
   echo "Your prompt here" > prompt.txt
   goose run prompt.txt
   ```

## Environment Variables

The following environment variables should be set before activating Flox:

- `ANTHROPIC_API_KEY` - Required for Claude models
- `OPENAI_API_KEY` - Optional, for OpenAI models
- `ACI_API_KEY` - Optional, for ACI services

## Configuration

The Goose configuration is stored in `~/.config/goose/profiles.yaml` and uses:
- Provider: Anthropic
- Model: claude-3-5-sonnet-20241022
- Toolkit: developer

## Troubleshooting

If you get API connection errors:
1. Verify your API keys are correctly set in the environment
2. Check that the keys are valid and have sufficient credits
3. Ensure you've sourced your .env file before activating Flox

## Security Note

Never commit your actual API keys to version control. Always use environment variables or secure secret management systems.