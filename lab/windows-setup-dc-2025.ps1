# PowerShell Setup Script for Windows Server 2025 Domain Controller

$ErrorActionPreference = "Stop"

Write-Host "[*] Setting up Windows Server 2025 Domain Controller..." -ForegroundColor Cyan

# Step 1: Install Active Directory Domain Services
Write-Host "[*] Installing Active Directory Domain Services..." -ForegroundColor Yellow
Install-WindowsFeature AD-Domain-Services, DNS -IncludeManagementTools

# Step 2: Configure Domain
Write-Host "[*] Configuring domain: cyber.lab" -ForegroundColor Yellow
$domainName = "cyber.lab"
$domainNetbios = "CYBER"
$adminPassword = ConvertTo-SecureString "P@ssw0rd2026!" -AsPlainText -Force

# Promote to Domain Controller
$params = @{
    DomainName                    = $domainName
    NewDomainNetbiosName          = $domainNetbios
    SafeModeAdministratorPassword = $adminPassword
    InstallDns                    = $true
    NoRebootOnCompletion          = $true
    Force                         = $true
}

Install-ADDSForest @params

# Step 3: Create OUs and Users
Write-Host "[*] Creating Organizational Units..." -ForegroundColor Yellow
New-ADOrganizationalUnit -Name "IT" -Path "dc=cyber,dc=lab"
New-ADOrganizationalUnit -Name "Finance" -Path "dc=cyber,dc=lab"
New-ADOrganizationalUnit -Name "HR" -Path "dc=cyber,dc=lab"
New-ADOrganizationalUnit -Name "Servers" -Path "dc=cyber,dc=lab"

# Step 4: Create test users
Write-Host "[*] Creating test users..." -ForegroundColor Yellow

$users = @(
    @{ Name = "Administrator"; Password = "P@ssw0rd2026!"; Group = "Domain Admins"; OU = "IT" },
    @{ Name = "LabAdmin"; Password = "P@ssw0rd2026!"; Group = "Domain Admins"; OU = "IT" },
    @{ Name = "ITManager"; Password = "Itman2026!"; Group = "Domain Admins"; OU = "IT" },
    @{ Name = "FinanceUser"; Password = "Finance2026!"; Group = "users"; OU = "Finance" },
    @{ Name = "HRUser"; Password = "HR2026!"; Group = "users"; OU = "HR" },
    @{ Name = "TestUser"; Password = "Test2026!"; Group = "users"; OU = "IT" }
)

foreach ($user in $users) {
    $path = "OU=$($user.OU),dc=cyber,dc=lab"
    $password = ConvertTo-SecureString $user.Password -AsPlainText -Force
    
    try {
        New-ADUser -Name $user.Name -SamAccountName $user.Name -AccountPassword $password `
            -Enabled $true -Path $path -PasswordNeverExpires $true -Verbose
        Add-ADGroupMember -Identity $user.Group -Members $user.Name -Verbose
        Write-Host "[+] User created: $($user.Name)" -ForegroundColor Green
    }
    catch {
        Write-Host "[-] Error creating user $($user.Name): $_" -ForegroundColor Red
    }
}

# Step 5: Create Groups
Write-Host "[*] Creating security groups..." -ForegroundColor Yellow

$groups = @(
    @{ Name = "IT-Admins"; Path = "OU=IT,dc=cyber,dc=lab" },
    @{ Name = "Finance-Team"; Path = "OU=Finance,dc=cyber,dc=lab" },
    @{ Name = "HR-Team"; Path = "OU=HR,dc=cyber,dc=lab" },
    @{ Name = "Exchange-Admins"; Path = "OU=IT,dc=cyber,dc=lab" }
)

foreach ($group in $groups) {
    try {
        New-ADGroup -Name $group.Name -GroupScope Global -Path $group.Path -Verbose
        Write-Host "[+] Group created: $($group.Name)" -ForegroundColor Green
    }
    catch {
        Write-Host "[-] Error creating group $($group.Name): $_" -ForegroundColor Red
    }
}

# Step 6: Configure DNS forwarders
Write-Host "[*] Configuring DNS..." -ForegroundColor Yellow
Set-DnsServerForwarder -IPAddress 8.8.8.8, 1.1.1.1 -PassThru

# Step 7: Enable Remote Desktop
Write-Host "[*] Enabling Remote Desktop..." -ForegroundColor Yellow
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0
Enable-NetFirewallRule -DisplayName "Remote Desktop - User Mode (TCP-In)"

# Step 8: Configure WinRM
Write-Host "[*] Configuring WinRM..." -ForegroundColor Yellow
Enable-PSRemoting -Force
Set-Item -Path 'WSMan:\localhost\Service\Auth\Basic' -Value $true

Write-Host "[+] Windows Server 2025 Domain Controller setup complete!" -ForegroundColor Green
Write-Host "[+] Domain: cyber.lab" -ForegroundColor Green
Write-Host "[+] Admin: LabAdmin / P@ssw0rd2026!" -ForegroundColor Green
Write-Host "[+] Users created: 6" -ForegroundColor Green
Write-Host "[+] Groups created: 4" -ForegroundColor Green

Write-Host "[!] System will reboot in 10 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Restart-Computer -Force
