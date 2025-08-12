# README_FLOX_GOOSE - Goose AI Agent with Flox Environment

This directory contains a Flox-based setup for the Goose AI agent, ensuring a portable and reproducible environment that works consistently across different devices.

## 🚀 Quick Start

1. **Install Flox** (if not already installed):
   ```bash
   curl -fsSL https://get.flox.dev | sh
   ```

2. **Set your API key**:
   ```bash
   export ANTHROPIC_API_KEY='your-anthropic-api-key'
   # OR
   export OPENAI_API_KEY='your-openai-api-key'
   ```

3. **Run the test script**:
   ```bash
   ./test_goose.sh
   ```

4. **Start Goose**:
   ```bash
   ./start-goose.sh
   ```

## 📁 Files

- `manifest.toml` - Flox environment configuration
- `test_goose.sh` - Test script to verify installation
- `start-goose.sh` - Script to start Goose in the Flox environment
- `goose-demo/` - Directory for Goose demo projects (created automatically)

## 🔧 How It Works

The Flox environment:
1. Creates an isolated Python virtual environment
2. Automatically installs Goose and all dependencies
3. Sets up proper paths and configurations
4. Provides a consistent environment regardless of system setup

## 💡 Benefits Over Local Installation

- **Portable**: Works on any system with Flox installed
- **Isolated**: No conflicts with system Python or other packages
- **Reproducible**: Same environment every time
- **Version-controlled**: Dependencies tracked in `manifest.toml`
- **No manual PATH configuration**: Everything is handled automatically

## 🛠️ Manual Flox Commands

If you prefer manual control:

```bash
# Activate the environment
cd goose && flox activate

# Once activated, run Goose commands directly
goose configure
goose session
goose --help

# Start as a service (optional)
flox services start goose-session
```

## 🔄 Updating Goose

To update Goose to the latest version:

```bash
cd goose
GOOSE_UPDATE=true flox activate
```

## 📝 Configuration

The Goose configuration is stored in `~/.config/goose/settings.json` and persists across sessions.

## 🐛 Troubleshooting

1. **Flox not found**: Install Flox from https://flox.dev/docs/install
2. **API key issues**: Ensure your API key is exported in your shell
3. **Permission errors**: Make scripts executable with `chmod +x *.sh`
4. **Python issues**: The Flox environment handles Python installation automatically

## 📚 Resources

- [Goose Documentation](https://github.com/block/goose)
- [Flox Documentation](https://flox.dev/docs)
- [Original Setup Guide](../README_GOOSE.md)