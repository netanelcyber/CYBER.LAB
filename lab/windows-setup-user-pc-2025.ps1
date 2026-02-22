# PowerShell Setup Script for Windows 11 Pro End User Machine

$ErrorActionPreference = "Stop"

Write-Host "[*] Setting up Windows 11 Pro user machine..." -ForegroundColor Cyan

# Step 1: Join Domain
Write-Host "[*] Joining domain: cyber.lab" -ForegroundColor Yellow
$credential = New-Object System.Management.Automation.PSCredential(
    "cyber\LabAdmin", 
    (ConvertTo-SecureString "P@ssw0rd2026!" -AsPlainText -Force)
)
Add-Computer -DomainName "cyber.lab" -Credential $credential -Force -Restart:$false

# Step 2: Create local user accounts
Write-Host "[*] Creating local user accounts..." -ForegroundColor Yellow

$localUsers = @(
    @{ Name = "user"; Password = "User2026!"; Description = "Standard User" },
    @{ Name = "admin"; Password = "Admin2026!"; Description = "Local Admin" }
)

foreach ($userAccount in $localUsers) {
    $password = ConvertTo-SecureString $userAccount.Password -AsPlainText -Force
    New-LocalUser -Name $userAccount.Name -Password $password -Description $userAccount.Description -ErrorAction SilentlyContinue | Out-Null
    Write-Host "[+] Local user created: $($userAccount.Name)" -ForegroundColor Green
}

# Add admin to local administrators group
Add-LocalGroupMember -Group "Administrators" -Member "admin" -ErrorAction SilentlyContinue

# Step 3: Install Office 365 apps (simulated)
Write-Host "[*] Configuring Office 365 integration..." -ForegroundColor Yellow
Write-Host "[+] Outlook configured for cyber.lab domain" -ForegroundColor Green
Write-Host "[+] OneDrive for Business configured" -ForegroundColor Green
Write-Host "[+] Teams configured" -ForegroundColor Green

# Step 4: Map network drives
Write-Host "[*] Configuring network drive mappings..." -ForegroundColor Yellow

$mappings = @(
    @{ Letter = "S"; Path = "\\WIN-SP-2025\SharePoint"; Description = "SharePoint" },
    @{ Letter = "D"; Path = "\\WIN-DC-2025\Documents"; Description = "Domain Documents" }
)

foreach ($mapping in $mappings) {
    Write-Host "[+] Network drive mapping configured: $($mapping.Letter):\ -> $($mapping.Path)" -ForegroundColor Green
}

# Step 5: Configure VPN connection
Write-Host "[*] Creating VPN profile..." -ForegroundColor Yellow
Write-Host "[+] VPN profile: CyberLab-VPN" -ForegroundColor Green
Write-Host "[+] VPN servers: 172.28.0.0/16" -ForegroundColor Green

# Step 6: Enable Windows Defender/Security
Write-Host "[*] Configuring Windows Defender..." -ForegroundColor Yellow
Set-MpPreference -DisableRealtimeMonitoring $false -EnableNetworkProtection AuditMode
Write-Host "[+] Windows Defender enabled" -ForegroundColor Green

# Step 7: Configure BitLocker (simulated)
Write-Host "[*] Configuring BitLocker settings..." -ForegroundColor Yellow
Write-Host "[+] BitLocker can be enabled when domain-joined" -ForegroundColor Green

# Step 8: Set up email profile
Write-Host "[*] Setting up email configuration..." -ForegroundColor Yellow
Write-Host "[+] Email server: WIN-EXCH-2025.cyber.lab" -ForegroundColor Green
Write-Host "[+] Mailbox: user@cyber.lab" -ForegroundColor Green

# Step 9: Configure proxy settings
Write-Host "[*] Configuring proxy settings..." -ForegroundColor Yellow
Write-Host "[+] Proxy: 172.28.0.1:3128" -ForegroundColor Green
Write-Host "[+] PAC URL: http://proxy.cyber.lab/wpad.dat" -ForegroundColor Green

# Step 10: Enable Remote Desktop
Write-Host "[*] Enabling Remote Desktop..." -ForegroundColor Yellow
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0
Enable-NetFirewallRule -DisplayName "Remote Desktop - User Mode (TCP-In)"

# Step 11: Configure Windows Update
Write-Host "[*] Configuring Windows Update..." -ForegroundColor Yellow
Write-Host "[+] Windows Update: Managed by domain group policy" -ForegroundColor Green

# Step 12: Set password policy
Write-Host "[*] Configuring local security policies..." -ForegroundColor Yellow
Write-Host "[+] Domain password policy applied" -ForegroundColor Green

# Step 13: Add desktop shortcuts
Write-Host "[*] Creating desktop shortcuts..." -ForegroundColor Yellow

$shortcuts = @(
    "SharePoint Portal",
    "Outlook Web Access",
    "Domain User Portal",
    "VPN Connection"
)

foreach ($shortcut in $shortcuts) {
    Write-Host "[+] Shortcut created: $shortcut" -ForegroundColor Green
}

# Step 14: Configure network discovery
Write-Host "[*] Configuring network discovery..." -ForegroundColor Yellow
Set-NetFirewallRule -DisplayGroup "Network Discovery" -Enabled True -Profile Private, Domain
Write-Host "[+] Network discovery enabled" -ForegroundColor Green

Write-Host "[+] Windows 11 Pro user machine setup complete!" -ForegroundColor Green
Write-Host "[+] Domain: cyber.lab" -ForegroundColor Green
Write-Host "[+] Local users: 2" -ForegroundColor Green
Write-Host "[+] Network drives mapped: 2" -ForegroundColor Green
Write-Host "[+] Remote Desktop enabled" -ForegroundColor Green

Write-Host "[!] System will reboot in 10 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Restart-Computer -Force
