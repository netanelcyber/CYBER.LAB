# PowerShell Setup Script for Windows Server 2025 Honeypot

$ErrorActionPreference = "Stop"

Write-Host "[*] Setting up Windows Server 2025 Honeypot..." -ForegroundColor Cyan

# Step 1: Install basic services
Write-Host "[*] Installing honeypot services..." -ForegroundColor Yellow
Install-WindowsFeature Web-Server, Web-WebServer, SMTP-Service, Telnet-Client

# Step 2: Create honeypot directories
Write-Host "[*] Creating honeypot data directories..." -ForegroundColor Yellow

$directories = @(
    "C:\Honeypot",
    "C:\Honeypot\fake_documents",
    "C:\Honeypot\fake_databases",
    "C:\Honeypot\logs"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}

# Step 3: Create fake sensitive documents
Write-Host "[*] Creating fake sensitive documents..." -ForegroundColor Yellow

$fakeDocuments = @(
    @{ File = "Credentials.txt"; Content = "admin:P@ssw0rd`nexchange:Exchange2025" },
    @{ File = "Database_Backup.sql"; Content = "-- Database backup`nCREATE TABLE users..." },
    @{ File = "Private_Key.pem"; Content = "-----BEGIN PRIVATE KEY-----`nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDL..." },
    @{ File = "VPN_Config.ovpn"; Content = "client`ndev tun`nproto tcp`nremote 172.28.0.1 1194" },
    @{ File = "SystemConfig.xml"; Content = "<config>`n<admin>honeypot_user</admin>`n<password>honeypot123</password>" },
    @{ File = "API_Keys.txt"; Content = "AWS_KEY=AKIAIOSFODNN7EXAMPLE`nAZURE_KEY=abcd1234..." }
)

foreach ($doc in $fakeDocuments) {
    $filePath = "C:\Honeypot\fake_documents\$($doc.File)"
    Set-Content -Path $filePath -Value $doc.Content -Force
    Write-Host "[+] Fake document created: $($doc.File)" -ForegroundColor Green
}

# Step 4: Create fake database structure
Write-Host "[*] Creating fake database structure..." -ForegroundColor Yellow

@"
USE master;
CREATE DATABASE honeypot_db;
USE honeypot_db;
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    salary INT,
    password VARCHAR(100)
);
INSERT INTO employees VALUES 
(1, 'Admin', 'admin@honeypot.com', 150000, 'P@ssw0rd123'),
(2, 'User', 'user@honeypot.com', 75000, 'User123456');
"@ | Set-Content -Path "C:\Honeypot\fake_databases\honeypot.sql" -Force

Write-Host "[+] Fake database created" -ForegroundColor Green

# Step 5: Create web application
Write-Host "[*] Creating honeypot web application..." -ForegroundColor Yellow

@"
<%@ Page Language="C#" %>
<%
    // Fake login page with vulnerability
    if(Request.Method == "POST") {
        string username = Request.Form["username"];
        string password = Request.Form["password"];
        
        // Log attempt (honeypot monitoring)
        System.IO.File.AppendAllText("C:\\Honeypot\\logs\\access.log", 
            DateTime.Now + " - Login attempt: " + username + "\r\n");
        
        Response.Redirect("admin.aspx?user=" + username);
    }
%>
<html>
<head><title>Admin Portal</title></head>
<body>
<h1>System Administration</h1>
<form method="POST">
    Username: <input type="text" name="username" /><br>
    Password: <input type="password" name="password" /><br>
    <input type="submit" value="Login" />
</form>
</body>
</html>
"@ | Set-Content -Path "C:\inetpub\wwwroot\index.aspx" -Force

Write-Host "[+] Honeypot web app created" -ForegroundColor Green

# Step 6: Configure IIS
Write-Host "[*] Configuring IIS for honeypot..." -ForegroundColor Yellow

New-WebSite -Name "honeypot" -PhysicalPath "C:\inetpub\wwwroot" -Port 8000 -HostHeader "honeypot.local" -ErrorAction SilentlyContinue | Out-Null
Write-Host "[+] IIS website created: honeypot (port 8000)" -ForegroundColor Green

# Step 7: Enable file sharing with weak permissions
Write-Host "[*] Creating network shares with weak permissions..." -ForegroundColor Yellow

New-SmbShare -Name "Documents" -Path "C:\Honeypot\fake_documents" -FullAccess "Everyone" -ErrorAction SilentlyContinue | Out-Null
New-SmbShare -Name "Databases" -Path "C:\Honeypot\fake_databases" -FullAccess "Everyone" -ErrorAction SilentlyContinue | Out-Null
Write-Host "[+] SMB shares created with full public access" -ForegroundColor Green

# Step 8: Create fake services
Write-Host "[*] Creating fake services..." -ForegroundColor Yellow

$ScriptBlock = {
    while($true) {
        Start-Sleep -Seconds 3600
    }
}

Register-ScheduledJob -Name "honeypot-monitor" -ScriptBlock $ScriptBlock -Trigger (New-JobTrigger -AtStartup) -ErrorAction SilentlyContinue | Out-Null
Write-Host "[+] Honeypot monitor service registered" -ForegroundColor Green

# Step 9: Enable logging
Write-Host "[*] Enabling comprehensive logging..." -ForegroundColor Yellow

# Enable Windows event logging
wevtutil.exe set-log Security /enabled:true
wevtutil.exe set-log System /enabled:true
Write-Host "[+] Windows Event Logging enabled" -ForegroundColor Green

# Step 10: Create honeypot users
Write-Host "[*] Creating honeypot user accounts..." -ForegroundColor Yellow

$honeypotUsers = @(
    @{ Name = "admin"; Password = "P@ssw0rd123"; Role = "Administrator" },
    @{ Name = "database"; Password = "db123456"; Role = "User" },
    @{ Name = "app"; Password = "appdata789"; Role = "User" }
)

foreach ($user in $honeypotUsers) {
    $password = ConvertTo-SecureString $user.Password -AsPlainText -Force
    New-LocalUser -Name $user.Name -Password $password -Description $user.Role -ErrorAction SilentlyContinue | Out-Null
    
    if($user.Role -eq "Administrator") {
        Add-LocalGroupMember -Group "Administrators" -Member $user.Name -ErrorAction SilentlyContinue
    }
    
    Write-Host "[+] Honeypot user created: $($user.Name) ($($user.Role))" -ForegroundColor Green
}

# Step 11: Configure firewall with open ports
Write-Host "[*] Configuring firewall..." -ForegroundColor Yellow

$ports = @(21, 23, 25, 53, 110, 143, 389, 445, 1433, 3306, 3389, 8000, 8080, 8443)
foreach ($port in $ports) {
    New-NetFirewallRule -DisplayName "Honeypot - Port $port" -Direction Inbound `
        -Action Allow -Protocol TCP -LocalPort $port -ErrorAction SilentlyContinue | Out-Null
    Write-Host "[+] Firewall rule for port $port" -ForegroundColor Green
}

# Step 12: Enable Remote Desktop
Write-Host "[*] Enabling Remote Desktop..." -ForegroundColor Yellow
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0
Write-Host "[+] Remote Desktop enabled" -ForegroundColor Green

# Step 13: Start monitoring
Write-Host "[*] Starting honeypot monitoring..." -ForegroundColor Yellow
Write-Host "[+] Accessing any resource will be logged to: C:\Honeypot\logs\" -ForegroundColor Green

Write-Host "[+] Windows Server 2025 Honeypot setup complete!" -ForegroundColor Green
Write-Host "[+] Fake documents: 6" -ForegroundColor Green
Write-Host "[+] Fake databases: 1" -ForegroundColor Green
Write-Host "[+] Web application: honeypot.local:8000" -ForegroundColor Green
Write-Host "[+] Network shares: 2 (Documents, Databases)" -ForegroundColor Green
Write-Host "[+] Honeypot users: 3" -ForegroundColor Green
Write-Host "[+] Monitoring enabled" -ForegroundColor Green

Write-Host "[!] Honeypot ready to log attacker activities!" -ForegroundColor Yellow
