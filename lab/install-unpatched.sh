#!/bin/bash
# Install unpatched and vulnerable services on Ubuntu 16.04

set -e

echo "[*] Installing unpatched services..."

# Update repositories (but not packages - keep vulnerable versions)
apt-get update

# Install vulnerable OpenSSH 7.2
apt-get install -y openssh-server=1:7.2p2-4ubuntu2.10
sed -i 's/#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
service ssh start

# Install vulnerable Apache 2.4.18
apt-get install -y apache2=2.4.18-1ubuntu3
a2enmod rewrite
a2enmod proxy
a2enmod proxy_http
service apache2 start

# Install vulnerable PHP 5.6
apt-get install -y php5=5.6.40-37ubuntu0.1
echo '<?php phpinfo(); ?>' > /var/www/html/info.php
service apache2 restart

# Install vulnerable MySQL client
apt-get install -y mysql-client=5.7.40-0ubuntu0.16.04.1

# Install curl with vulnerable OpenSSL
apt-get install -y curl=7.47.0-1ubuntu1

# Install vulnerable Node.js
apt-get install -y nodejs=4.2.6~dfsg-1ubuntu4.2
apt-get install -y npm

# Create vulnerable web app
mkdir -p /var/www/vulnerable-app
cat > /var/www/vulnerable-app/index.php << 'EOF'
<?php
echo "<h1>Unpatched Vulnerable System</h1>";
echo "<p>System Information:</p>";
echo "OpenSSH Version: " . shell_exec("ssh -V 2>&1") . "<br>";
echo "Apache Version: " . shell_exec("apache2ctl -v 2>&1 | head -1") . "<br>";
echo "PHP Version: " . phpversion() . "<br>";

// Intentional SQL injection vulnerability
if(isset($_GET['user'])) {
    $conn = new mysqli("localhost", "root", "", "vulnerable");
    $user = $_GET['user'];
    $query = "SELECT * FROM users WHERE username='" . $user . "'";
    $result = $conn->query($query);
    if($result) {
        while($row = $result->fetch_assoc()) {
            echo "User: " . $row['username'] . " - Email: " . $row['email'];
        }
    }
}

// RCE vulnerability
if(isset($_GET['cmd'])) {
    echo "<pre>";
    system($_GET['cmd']);
    echo "</pre>";
}
?>
EOF

chmod 755 /var/www/vulnerable-app/index.php

# Enable site
a2ensite 000-default
service apache2 restart

# Create default users
useradd -m -p $(openssl passwd -1 'password') testuser || true
useradd -m -p $(openssl passwd -1 'P@ssw0rd2026!') admin || true

# Start SSH
service ssh start

echo "[+] Unpatched system ready!"
echo "[+] SSH: ssh://localhost:22 (testuser/password or admin/P@ssw0rd2026!)"
echo "[+] HTTP: http://localhost:8080"
echo "[+] PHP Info: http://localhost:8080/info.php"

tail -f /dev/null
