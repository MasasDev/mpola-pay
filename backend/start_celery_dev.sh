#!/bin/bash

# Development mode - run Celery tasks synchronously without Redis
# Make this file executable: chmod +x start_celery_dev.sh

echo "🔧 Starting Mpola Pay in Development Mode (No Redis Required)..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up development environment...${NC}"

# Create a temporary settings file for development
cat > dev_settings.py << EOF
# Development settings that override production settings
from .settings import *

# Override Celery to run synchronously for development
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

print("🔧 Running in development mode - tasks will execute synchronously")
EOF

echo -e "${GREEN}✅ Development mode configured${NC}"
echo -e "${YELLOW}📋 In this mode:${NC}"
echo -e "   - Tasks run immediately without queueing"
echo -e "   - No Redis or message broker required"
echo -e "   - Perfect for testing and development"
echo -e "   - Use the regular Django server: python manage.py runserver"

echo -e "\n${BLUE}To use development mode:${NC}"
echo -e "${YELLOW}export DJANGO_SETTINGS_MODULE=mpola.dev_settings${NC}"
echo -e "${YELLOW}python manage.py runserver${NC}"
