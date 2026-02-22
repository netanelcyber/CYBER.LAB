# Lab Environment Setup - CYBER.LAB

## Overview

This directory contains Docker-based vulnerable lab environments for **authorized security testing and learning only**.

🔒 **IMPORTANT SECURITY NOTE:**
- These environments are **intentionally vulnerable** 
- Use ONLY in isolated lab networks
- Never expose to the internet
- Only for authorized penetration testing or educational purposes
- Always follow Rules of Engagement

---

## What's Included

### Lab Environments

1. **Drupal 7.x (Vulnerable)**
   - Known vulnerabilities: 45+ CVEs
   - Vulnerable modules pre-configured
   - Drupalgeddon 2, Views RCE, Entity API exploits
   - MySQL database
   - HTTP on port 8001

2. **WordPress (Vulnerable)**
   - Vulnerable plugins pre-configured
   - Elementor RCE, File Manager exploits
   - WooCommerce SQL injection
   - MySQL database
   - HTTP on port 8002

3. **RADWARE WAF Simulator**
   - Mock WAF protection
   - Rule-based filtering
   - CAPTCHA simulation
   - Rate limiting simulation
   - Access on port 8000

4. **ELK Monitoring Stack**
   - Elasticsearch for log storage
   - Kibana for visualization
   - Real-time access to all HTTP requests
   - Forensic evidence collection

---

## Quick Start

```bash
# 1. Setup and start all services
./setup.sh

# 2. Install vulnerable modules/plugins
./install-drupal-modules.sh
./install-wordpress-plugins.sh

# 3. View testing guide
cat LAB_TESTING_GUIDE.md

# 4. Start testing!
cd ../
python scripts/drupal_cve_scanner.py http://localhost:8001
```

---

## Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | All service definitions |
| `radware-nginx.conf` | RADWARE WAF simulator rules |
| `setup.sh` | Initialization and startup script |
| `install-drupal-modules.sh` | Install vulnerable Drupal modules |
| `install-wordpress-plugins.sh` | Install vulnerable WordPress plugins |
| `LAB_TESTING_GUIDE.md` | Detailed testing scenarios |
| `.gitignore` | Exclude volumes/sensitive data |

---

## Access URLs

| Service | URL | User | Pass |
|---------|-----|------|------|
| Drupal 7 | http://localhost:8001 | admin | admin |
| WordPress | http://localhost:8002 | admin | admin |
| RADWARE WAF | http://localhost:8000 | - | - |
| Kibana | http://localhost:5601 | - | - |

---

## Testing with CYBER.LAB Scripts

### Drupal Vulnerability Scanner
```bash
python ../scripts/drupal_cve_scanner.py http://localhost:8001
```

### Privilege Escalation Exploitation
```bash
python ../scripts/drupal_privesc_exploit.py http://localhost:8001
```

### Configuration Extraction
```bash
python ../scripts/drupal_config_extractor.py http://localhost:8001
```

---

## Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (databases)
docker-compose down -v

# Remove all Docker containers
docker-compose rm -f
```

---

## Useful Commands

```bash
# View logs
docker-compose logs -f

# Access Drupal container
docker exec -it drupal7-app bash

# Access database
docker exec -it drupal7-db mysql -u drupal -pdrupal123456 drupal

# View nginx access logs
docker logs radware-simulator

# Check service health
docker-compose ps

# Restart specific service
docker-compose restart drupal7-app
```

---

## Lab Scenarios

See `LAB_TESTING_GUIDE.md` for detailed testing scenarios:

1. SQL Injection Testing
2. RADWARE WAF Bypass Testing
3. Views Module RCE
4. Entity API Privilege Escalation
5. File Upload RCE
6. WordPress Plugin Exploitation
7. RADWARE WAF Bypass Vectors
8. Monitoring & Evidence Collection

---

## Learning Objectives

By using this lab, you will learn:

✓ How Drupal 7.x vulnerabilities work  
✓ How to identify and exploit CVEs  
✓ WAF bypass techniques and limitations  
✓ Privilege escalation attack chains  
✓ Configuration file security risks  
✓ REST API security issues  
✓ Evidence collection and forensics  
✓ Incident response procedures  

---

## Legal & Ethical Guidelines

⚠️ **Use responsibly:**

- ✅ DO use for learning and authorized testing
- ✅ DO practice security concepts in isolation
- ✅ DO develop better defense strategies
- ❌ DON'T attack real systems without permission
- ❌ DON'T use for malicious purposes
- ❌ DON'T expose to public internet
- ❌ DON'T share vulnerable infrastructure details publicly

---

## Support & Documentation

- Full testing guide: `LAB_TESTING_GUIDE.md`
- Docker Compose reference: https://docs.docker.com/compose/
- Drupal security: https://www.drupal.org/security
- WordPress security: https://wordpress.org/support/article/hardening-wordpress/

---

**Last Updated:** February 22, 2026  
**Status:** Ready for authorized security testing  
**Classification:** For learning and authorized pentest use only

