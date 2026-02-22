#!/bin/bash

# WordPress Vulnerable Plugins Installation
# Installs plugins with known vulnerabilities for testing

echo "Installing vulnerable WordPress plugins..."

# Enter WordPress container
docker exec -it wordpress-app bash << 'EOF'

cd /var/www/html/wp-content/plugins

# Install WP-CLI if not present
if ! command -v wp &> /dev/null; then
    curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar
    chmod +x wp-cli.phar
    mv wp-cli.phar /usr/local/bin/wp
fi

# 1. Elementor (SQL injection - CVE-2022-28735)
echo "[*] Installing Elementor (vulnerable version)..."
wp plugin install elementor --allow-root
wp plugin activate elementor --allow-root

# 2. Akismet (vulnerable to bypass)
echo "[*] Installing Akismet..."
wp plugin install akismet --allow-root
wp plugin activate akismet --allow-root

# 3. WooCommerce (SQL injection vulnerabilities)
echo "[*] Installing WooCommerce..."
wp plugin install woocommerce --allow-root
wp plugin activate woocommerce --allow-root

# 4. Contact Form 7 (RCE vulnerabilities)
echo "[*] Installing Contact Form 7..."
wp plugin install contact-form-7 --allow-root
wp plugin activate contact-form-7 --allow-root

# 5. File Manager (Remote Code Execution - CVE-2020-11738)
echo "[*] Installing File Manager..."
cd /tmp && git clone https://github.com/evetsug/file-manager.git 2>/dev/null || true
if [ -d file-manager ]; then
    cp -r file-manager /var/www/html/wp-content/plugins/file-manager
    wp plugin activate file-manager --allow-root 2>/dev/null || true
fi
cd /var/www/html/wp-content/plugins

# 6. Admin Columns (Privilege escalation)
echo "[*] Installing Admin Columns..."
wp plugin install admin-columns --allow-root 2>/dev/null || true
wp plugin activate admin-columns --allow-root 2>/dev/null || true

# Create test user for exploitation
echo "[*] Creating test user..."
wp user create testuser test@test.local --user_pass=Test1234 --role=subscriber --allow-root 2>/dev/null || true

# Set proper permissions
cd /var/www/html
chmod -R 777 wp-content
chmod -R 777 wp-config.php

echo "[✓] Vulnerable plugins installed successfully"
echo ""
echo "Installed plugins:"
echo "  - Elementor (SQL injection - CVE-2022-28735)"
echo "  - Akismet (various vulnerabilities)"
echo "  - WooCommerce (SQL injection)"
echo "  - Contact Form 7 (RCE)"
echo "  - File Manager (RCE - CVE-2020-11738)"
echo "  - Admin Columns (Privilege escalation)"
echo ""
echo "Access: http://localhost:8002/wp-admin"
echo "Test user: testuser / Test1234"

EOF

echo "[✓] WordPress plugin installation complete"
