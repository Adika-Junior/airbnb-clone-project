#!/bin/bash
# Setup script for Airbnb Clone Project
# This script sets up the complete project with all ALX services integrated

set -e  # Exit on error

echo "🚀 Setting up Airbnb Clone Project..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from template...${NC}"
    cp env.example .env
    echo -e "${GREEN}✓ .env file created. Please update it with your settings.${NC}"
fi

# Generate secret key if not set
if ! grep -q "SECRET_KEY=" .env || grep -q "SECRET_KEY=your-super-secret-key" .env; then
    echo -e "${YELLOW}Generating SECRET_KEY...${NC}"
    SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    fi
    echo -e "${GREEN}✓ SECRET_KEY generated and added to .env${NC}"
fi

# Run migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
echo ""
echo -e "${YELLOW}Would you like to create a superuser? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py createsuperuser
fi

# Collect static files
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Update .env file with your database and service configurations"
echo "2. Start Redis: redis-server (or use Docker)"
echo "3. Start RabbitMQ: rabbitmq-server (or use Docker)"
echo "4. Start Celery worker: celery -A airbnb_clone worker --loglevel=info"
echo "5. Start Celery beat: celery -A airbnb_clone beat --loglevel=info"
echo "6. Start Django server: python manage.py runserver"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up -d"
echo ""
echo "Access the application at:"
echo "  - Main: http://localhost:8000"
echo "  - Admin: http://localhost:8000/admin/"
echo "  - Swagger: http://localhost:8000/swagger/"
echo "  - GraphQL: http://localhost:8000/graphql/"
