#!/bin/bash

# Drupal 7 Vulnerable Modules Installation
# Installs modules with known vulnerabilities for testing

echo "Installing vulnerable Drupal 7 modules..."

# Enter Drupal container
docker exec -it drupal7-app bash << 'EOF'

cd /var/www/html

# Enable Drush for module management
curl -sS https://getcomposer.org/installer | php
php composer.phar require drush/drush:^8

# Install vulnerable modules

# 1. Views module (CVE-2020-13662)
echo "[*] Installing Views module..."
curl -L https://ftp.drupal.org/files/projects/views-7.x-3.20.tar.gz | tar xz -C sites/all/modules/
drush en -y views

# 2. Services module (CVE-2019-9735)
echo "[*] Installing Services module..."
curl -L https://ftp.drupal.org/files/projects/services-7.x-3.23.tar.gz | tar xz -C sites/all/modules/
drush en -y services

# 3. Ctools (dependency for many exploits)
echo "[*] Installing Ctools..."
curl -L https://ftp.drupal.org/files/projects/ctools-7.x-1.14.tar.gz | tar xz -C sites/all/modules/
drush en -y ctools

# 4. Features module (dependency)
echo "[*] Installing Features..."
curl -L https://ftp.drupal.org/files/projects/features-7.x-2.12.tar.gz | tar xz -C sites/all/modules/
drush en -y features

# 5. Entity API (for entity manipulation exploits)
echo "[*] Installing Entity API..."
curl -L https://ftp.drupal.org/files/projects/entity-7.x-1.9.tar.gz | tar xz -C sites/all/modules/
drush en -y entity

# 6. File Entity (file upload vulnerabilities)
echo "[*] Installing File Entity..."
curl -L https://ftp.drupal.org/files/projects/file_entity-7.x-2.24.tar.gz | tar xz -C sites/all/modules/
drush en -y file_entity

# Set permissions for exploitation
chmod -R 777 sites/default/files
chmod 777 sites/default

echo "[✓] Vulnerable modules installed successfully"
echo ""
echo "Installed modules:"
echo "  - Views (CVE-2020-13662)"
echo "  - Services (CVE-2019-9735)"
echo "  - CTools (dependencies)"
echo "  - Features (dependencies)"
echo "  - Entity API (for entity manipulation)"
echo "  - File Entity (file upload exploits)"
echo ""
echo "Access: http://localhost:8001/admin/modules"

EOF

echo "[✓] Drupal module installation complete"
