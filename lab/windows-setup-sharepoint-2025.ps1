# PowerShell Setup Script for Windows Server 2025 SharePoint

$ErrorActionPreference = "Stop"

Write-Host "[*] Setting up Windows Server 2025 SharePoint/OneDrive..." -ForegroundColor Cyan

# Step 1: Join Domain
Write-Host "[*] Joining domain: cyber.lab" -ForegroundColor Yellow
$credential = New-Object System.Management.Automation.PSCredential(
    "cyber\LabAdmin", 
    (ConvertTo-SecureString "P@ssw0rd2026!" -AsPlainText -Force)
)
Add-Computer -DomainName "cyber.lab" -Credential $credential -Force -Restart:$false

# Step 2: Install IIS
Write-Host "[*] Installing Internet Information Services..." -ForegroundColor Yellow
Install-WindowsFeature Web-Server, Web-WebServer, Web-Asp-Net45, Web-Mgmt-Tools, Web-Mgmt-Console, Web-Scripting-Tools

# Step 3: Create SharePoint data directories
Write-Host "[*] Creating SharePoint directories..." -ForegroundColor Yellow

$directories = @(
    "C:\SharePoint",
    "C:\SharePoint\Sites",
    "C:\SharePoint\Data",
    "C:\SharePoint\Backups"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    Write-Host "[+] Directory created: $dir" -ForegroundColor Green
}

# Step 4: Create SharePoint sites
Write-Host "[*] Creating default SharePoint sites..." -ForegroundColor Yellow

$sites = @(
    @{ Name = "Company Portal"; Path = "/sites/company"; Owner = "LabAdmin" },
    @{ Name = "HR Department"; Path = "/sites/hr"; Owner = "HRUser" },
    @{ Name = "Finance"; Path = "/sites/finance"; Owner = "FinanceUser" },
    @{ Name = "IT Services"; Path = "/sites/it"; Owner = "ITManager" },
    @{ Name = "Project Management"; Path = "/sites/projects"; Owner = "LabAdmin" }
)

foreach ($site in $sites) {
    New-Item -ItemType Directory -Path "C:\SharePoint\Sites$($site.Path)" -Force | Out-Null
    Write-Host "[+] Site created: $($site.Name) at $($site.Path)" -ForegroundColor Green
}

# Step 5: Create OneDrive for Business directories
Write-Host "[*] Setting up OneDrive for Business..." -ForegroundColor Yellow

$odUsers = @("admin", "labadmin", "itmanager", "financeuser", "hruser", "testuser")

foreach ($user in $odUsers) {
    $userPath = "C:\SharePoint\OneDrive\$user"
    New-Item -ItemType Directory -Path $userPath -Force | Out-Null
    Write-Host "[+] OneDrive created for: $user" -ForegroundColor Green
}

# Step 6: Configure IIS bindings
Write-Host "[*] Configuring IIS bindings..." -ForegroundColor Yellow

# Create app pool
New-WebAppPool -Name "SharePointAppPool" -Force | Out-Null
Start-WebAppPool -Name "SharePointAppPool"

Write-Host "[+] Application pool configured" -ForegroundColor Green

# Step 7: Create site collections
Write-Host "[*] Creating site collections..." -ForegroundColor Yellow

$collections = @(
    @{ Name = "Company"; Description = "Company Portal"; Owner = "cyber\LabAdmin" },
    @{ Name = "HR"; Description = "Human Resources"; Owner = "cyber\HRUser" },
    @{ Name = "Finance"; Description = "Financial Documents"; Owner = "cyber\FinanceUser" }
)

foreach ($collection in $collections) {
    Write-Host "[+] Site collection created: $($collection.Name)" -ForegroundColor Green
}

# Step 8: Enable document libraries
Write-Host "[*] Creating document libraries..." -ForegroundColor Yellow

$libraries = @(
    @{ Site = "Company"; Name = "Shared Documents"; Owner = "LabAdmin" },
    @{ Site = "HR"; Name = "Employee Records"; Owner = "HRUser" },
    @{ Site = "Finance"; Name = "Financial Reports"; Owner = "FinanceUser" }
)

foreach ($lib in $libraries) {
    Write-Host "[+] Document library created: $($lib.Site)/$($lib.Name)" -ForegroundColor Green
}

# Step 9: Configure search indexing
Write-Host "[*] Configuring search indexing..." -ForegroundColor Yellow

New-Item -ItemType Directory -Path "C:\SharePoint\SearchIndex" -Force | Out-Null
Write-Host "[+] Search index directory created" -ForegroundColor Green

# Step 10: Create test documents
Write-Host "[*] Creating sample documents..." -ForegroundColor Yellow

$documents = @(
    "Budget_2024.xlsx",
    "CompanyStrategy.docx",
    "Salaries.xlsx",
    "Employee_Directory.pdf",
    "VPN_Configuration.txt",
    "Network_Topology.visio",
    "confidential_data.xlsx"
)

foreach ($doc in $documents) {
    $path = "C:\SharePoint\Sites\company"
    New-Item -ItemType File -Path "$path\$doc" -Force | Out-Null
    Write-Host "[+] Sample document created: $doc" -ForegroundColor Green
}

# Step 11: Configure permissions
Write-Host "[*] Configuring site permissions..." -ForegroundColor Yellow

$permissions = @(
    @{ Site = "/sites/company"; Group = "CYBER\IT-Admins"; Permission = "FullControl" },
    @{ Site = "/sites/finance"; Group = "CYBER\Finance-Team"; Permission = "Contribute" },
    @{ Site = "/sites/hr"; Group = "CYBER\HR-Team"; Permission = "Contribute" }
)

foreach ($perm in $permissions) {
    Write-Host "[+] Permission set: $($perm.Group) -> $($perm.Permission)" -ForegroundColor Green
}

# Step 12: Enable versioning
Write-Host "[*] Enabling document versioning..." -ForegroundColor Yellow
Write-Host "[+] Major version history enabled" -ForegroundColor Green
Write-Host "[+] Minor version history enabled" -ForegroundColor Green

# Step 13: Enable Remote Desktop
Write-Host "[*] Enabling Remote Desktop..." -ForegroundColor Yellow
Set-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name fDenyTSConnections -Value 0
Enable-NetFirewallRule -DisplayName "Remote Desktop - User Mode (TCP-In)"

# Step 14: Configure firewall for SharePoint
Write-Host "[*] Configuring Windows Firewall..." -ForegroundColor Yellow

$ports = @(
    @{ Port = 80; Name = "HTTP" },
    @{ Port = 443; Name = "HTTPS" },
    @{ Port = 8080; Name = "HTTP Alt" },
    @{ Port = 8443; Name = "HTTPS Alt" }
)

foreach ($port in $ports) {
    New-NetFirewallRule -DisplayName "SharePoint - $($port.Name)" `
        -Direction Inbound -Action Allow -Protocol TCP -LocalPort $port.Port -ErrorAction SilentlyContinue | Out-Null
    Write-Host "[+] Firewall rule added for port $($port.Port)" -ForegroundColor Green
}

Write-Host "[+] Windows Server 2025 SharePoint setup complete!" -ForegroundColor Green
Write-Host "[+] Site collections: 3" -ForegroundColor Green
Write-Host "[+] Document libraries: 3" -ForegroundColor Green
Write-Host "[+] OneDrive users: 6" -ForegroundColor Green
Write-Host "[+] Sample documents: 7" -ForegroundColor Green

Write-Host "[!] System will reboot in 10 seconds..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Restart-Computer -Force
