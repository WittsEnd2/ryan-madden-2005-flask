#!/bin/bash

# Setup script for development environment

echo "Setting up NFL Game Application..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env

    # Generate a secure SECRET_KEY
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

    # Update .env with generated SECRET_KEY
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here/$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
    fi

    echo "Generated secure SECRET_KEY in .env file"
else
    echo ".env file already exists, skipping..."
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python app.py"
echo ""
echo "Or use: ./scripts/dev.sh"
