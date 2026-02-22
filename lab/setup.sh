#!/bin/bash

# CYBER.LAB - Vulnerable Lab Setup Script
# Sets up Drupal 7.x + WordPress labs with RADWARE WAF simulator

set -e

echo "═══════════════════════════════════════════════════════════════"
echo "  CYBER.LAB - Vulnerable Lab Environment Setup"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Docker
echo "[*] Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[!] Docker not found. Please install Docker first.${NC}"
    exit 1
fi
echo -e "${GREEN}[✓] Docker found${NC}"

# Check Docker Compose
echo "[*] Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}[!] Docker Compose not found. Please install Docker Compose.${NC}"
    exit 1
fi
echo -e "${GREEN}[✓] Docker Compose found${NC}"

# Create lab directory if needed
if [ ! -d "lab" ]; then
    echo "[*] Creating lab directory..."
    mkdir -p lab
fi

# Navigate to lab directory
cd lab

# Pull images
echo ""
echo "[*] Pulling Docker images (this may take a few minutes)..."
docker-compose pull

# Start containers
echo ""
echo "[*] Starting lab containers..."
docker-compose up -d

# Wait for services to start
echo "[*] Waiting for services to initialize..."
sleep 10

# Check if services are running
echo ""
echo "[*] Checking service status..."
docker-compose ps

# Get container IPs
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Lab Environment Ready!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}[✓] Drupal 7.x Lab:${NC}"
echo "    URL: http://localhost:8001"
echo "    Database: drupal / drupal123456"
echo "    MySQL: localhost:3306"
echo ""
echo -e "${GREEN}[✓] WordPress Lab:${NC}"
echo "    URL: http://localhost:8002"
echo "    Database: wordpress / wordpress123456"
echo "    MySQL: localhost:3307"
echo ""
echo -e "${GREEN}[✓] RADWARE WAF Simulator:${NC}"
echo "    URL: http://localhost:8000"
echo "    Drupal via WAF: http://localhost:8000/drupal7/"
echo "    WordPress via WAF: http://localhost:8000/wordpress/"
echo ""
echo -e "${GREEN}[✓] Monitoring (ELK Stack):${NC}"
echo "    Kibana: http://localhost:5601"
echo "    Elasticsearch: http://localhost:9200"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Configure Drupal at http://localhost:8001 (admin/admin)"
echo "2. Configure WordPress at http://localhost:8002 (admin/admin)"
echo "3. Install vulnerable plugins/modules from ./scripts/"
echo "4. Run CYBER.LAB tools against the lab:"
echo "   python ../scripts/drupal_cve_scanner.py http://localhost:8001"
echo "5. Monitor requests in Kibana: http://localhost:5601"
echo ""
echo "To stop labs:"
echo "   docker-compose down"
echo ""
echo "To view logs:"
echo "   docker-compose logs -f"
echo ""
