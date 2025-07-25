#!/bin/bash

# Celery startup script for Mpola Pay
# Make this file executable: chmod +x start_celery.sh

echo "🚀 Starting Mpola Pay Celery Services..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Redis is running
echo -e "${BLUE}Checking Redis connection...${NC}"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not running. Please start Redis first:${NC}"
    echo -e "${YELLOW}   brew services start redis${NC}"
    echo -e "${YELLOW}   # OR${NC}"
    echo -e "${YELLOW}   redis-server${NC}"
    exit 1
fi

# Function to start Celery worker
start_worker() {
    echo -e "\n${BLUE}Starting Celery Worker...${NC}"
    PYTHONPATH=/Users/arthur/developer_zone/mpola-pay/backend celery -A mpola.celery worker --loglevel=info --pool=solo &
    WORKER_PID=$!
    echo -e "${GREEN}✅ Celery Worker started (PID: $WORKER_PID)${NC}"
}

# Function to start Celery beat scheduler
start_beat() {
    echo -e "\n${BLUE}Starting Celery Beat Scheduler...${NC}"
    PYTHONPATH=/Users/arthur/developer_zone/mpola-pay/backend celery -A mpola.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler &
    BEAT_PID=$!
    echo -e "${GREEN}✅ Celery Beat started (PID: $BEAT_PID)${NC}"
}

# Function to start Celery monitor (optional)
start_monitor() {
    echo -e "\n${BLUE}Starting Celery Monitor (Flower)...${NC}"
    if command -v flower &> /dev/null; then
        PYTHONPATH=/Users/arthur/developer_zone/mpola-pay/backend celery -A mpola.celery flower --port=5555 &
        FLOWER_PID=$!
        echo -e "${GREEN}✅ Celery Monitor (Flower) started (PID: $FLOWER_PID)${NC}"
        echo -e "${YELLOW}📊 Monitor available at: http://localhost:5555${NC}"
    else
        echo -e "${YELLOW}⚠️  Flower not installed. To install: pip install flower${NC}"
    fi
}

# Function to handle cleanup on script exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping Celery services...${NC}"
    if [ ! -z "$WORKER_PID" ]; then
        kill $WORKER_PID 2>/dev/null
        echo -e "${GREEN}✅ Celery Worker stopped${NC}"
    fi
    if [ ! -z "$BEAT_PID" ]; then
        kill $BEAT_PID 2>/dev/null
        echo -e "${GREEN}✅ Celery Beat stopped${NC}"
    fi
    if [ ! -z "$FLOWER_PID" ]; then
        kill $FLOWER_PID 2>/dev/null
        echo -e "${GREEN}✅ Celery Monitor stopped${NC}"
    fi
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start services
start_worker
start_beat
start_monitor

echo -e "\n${GREEN}🎉 All Celery services are running!${NC}"
echo -e "${BLUE}📝 Logs will appear below. Press Ctrl+C to stop all services.${NC}"
echo -e "${YELLOW}📋 Services:${NC}"
echo -e "   - Worker: Processing tasks"
echo -e "   - Beat: Scheduling periodic tasks"
echo -e "   - Monitor: http://localhost:5555 (if Flower is installed)"

# Wait for all background processes
wait
