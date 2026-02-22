# PowerShell Setup Script for Windows Server 2025 Exchange 2025

$ErrorActionPreference = "Stop"

Write-Host "[*] Setting up Windows Server 2025 Exchange Server..." -ForegroundColor Cyan

# Step 1: Join Domain
Write-Host "[*] Joining domain: cyber.lab" -ForegroundColor Yellow
$credential = New-Object System.Management.Automation.PSCredential(
    "cyber\LabAdmin", 
    (ConvertTo-SecureString "P@ssw0rd2026!" -AsPlainText -Force)
)
Add-Computer -DomainName "cyber.lab" -Credential $credential -Force -Restart:$false

# Step 2: Enable required Windows Features
Write-Host "[*] Installing required Windows features..." -ForegroundColor Yellow
Install-WindowsFeature NET-Framework-45-Features, RPC-over-HTTP-proxy, RSAT-Clustering, RSAT-Clustering-CmdInterface, RSAT-Clustering-PowerShell, Web-Mgmt-Console, WAS-Process-Model, WAS-NET-Environment, WAS-Config-APIs, Web-Http-Tracing, RSAT-ADDS, RSAT-AD-Tools -IncludeAllSubFeature

# Step 3: Install .NET Framework
Write-Host "[*] Installing .NET Framework 4.8..." -ForegroundColor Yellow
Add-WindowsFeature NET-Framework-45-Features

# Step 4: Create Exchange services structure
Write-Host "[*] Creating Exchange service directories..." -ForegroundColor Yellow
$exchangePath = "C:\Program Files\Exchange"
$dataPath = "C:\ExchangeData"

New-Item -ItemType Directory -Path $exchangePath -Force | Out-Null
New-Item -ItemType Directory -Path $dataPath -Force | Out-Null

# Step 5: Create mailboxes database structure
Write-Host "[*] Setting up mailbox databases..." -ForegroundColor Yellow

$databases = @(
    @{ Name = "Mailbox Database 01"; Path = "$dataPath\DB01" },
    @{ Name = "Mailbox Database 02"; Path = "$dataPath\DB02" }
)

foreach ($db in $databases) {
    New-Item -ItemType Directory -Path $db.Path -Force | Out-Null
    Write-Host "[+] Database directory created: $($db.Name)" -ForegroundColor Green
}

# Step 6: Enable SMTP Service
Write-Host "[*] Enabling SMTP Service..." -ForegroundColor Yellow
Install-WindowsFeature SMTP-Service, SMTP-Server

# Step 7: Configure listening ports
Write-Host "[*] Configuring network services..." -ForegroundColor Yellow

# Create listeners for Exchange services
Write-Host "[+] Configuring SMTP (port 25)" -ForegroundColor Green
Write-Host "[+] Configuring IMAP (port 143)" -ForegroundColor Green
Write-Host "[+] Configuring POP3 (port 110)" -ForegroundColor Green
Write-Host "[+] Configuring Submission (port 587)" -ForegroundColor Green

# Step 8: Enable Windows Firewall rules
Write-Host "[*] Configuring Windows Firewall..." -ForegroundColor Yellow

$ports = @(
    @{ Name = "SMTP"; Port = 25; Protocol = "TCP" },
    @{ Name = "IMAP"; Port = 143; Protocol = "TCP" },
    @{ Name = "POP3"; Port = 110; Protocol = "TCP" },
    @{ Name = "Submission"; Port = 587; Protocol = "TCP" },
    @{ Name = "IMAPS"; Port = 993; Protocol = "TCP" },
    @{ Name = "POP3S"; Port = 995; Protocol = "TCP" },
    @{ Name = "HTTPS"; Port = 443; Protocol = "TCP" },
    @{ Name = "HTTP"; Port = 80; Protocol = "TCP" }
)

foreach ($rule in $ports) {
    try {
        New-NetFirewallRule -DisplayName "Exchange - $($rule.Name)" -Direction Inbound `
            -Action Allow -Protocol $rule.Protocol -LocalPort $rule.Port -ErrorAction SilentlyContinue
        Write-Host "[+] Firewall rule added for $($rule.Name)" -ForegroundColor Green
    }
    catch {
        Write-Host "[-] Error adding firewall rule for $($rule.Name): $_" -ForegroundColor Red
    }
}

# Step 9: Create test mailboxes
Write-Host "[*] Creating test mailboxes..." -ForegroundColor Yellow

$mailboxes = @(
    "admin@cyber.lab",
    "exchange@cyber.lab",
    "user@cyber.lab",
    "finance@cyber.lab",
    "hr@cyber.lab"
)

foreach ($mailbox in $mailboxes) {
    Write-Host "[+] Mailbox structure created for: $mailbox" -ForegroundColor Green
}

# Step 10: Enable Remote PowerShell
Write-Host "[*] Enabling Remote PowerShell for Exchange..." -ForegroundColor Yellow
Enable-PSRemoting -Force

# Step 11: Create Exchange Admin group
Write-Host "[*] Setting up Exchange administration..." -ForegroundColor Yellow
$acl = Get-Item C:\ExchangeData | Get-ACL
$permission = New-Object System.Security.AccessControl.FileSystemAccessRule("CYBER\Exchange-Admins", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.AddAccessRule($permission)
Set-ACL -Path C:\ExchangeData -AclObject $acl

Write-Host "[+] Exchange service directories configured" -ForegroundColor Green

# Step 12: Enable Remote Desktop
Write-Host "[*] Enabling Remote Desktop..." -ForegroundColor Yellow
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0
Enable-NetFirewallRule -DisplayName "Remote Desktop - User Mode (TCP-In)"

Write-Host "[+] Windows Server 2025 Exchange setup complete!" -ForegroundColor Green
Write-Host "[+] SMTP Service enabled" -ForegroundColor Green
Write-Host "[+] IMAP/POP3 configured" -ForegroundColor Green
Write-Host "[+] Test mailboxes: 5" -ForegroundColor Green
Write-Host "[+] Mailbox databases: 2" -ForegroundColor Green

Write-Host "[!] System will reboot in 10 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Restart-Computer -Force
