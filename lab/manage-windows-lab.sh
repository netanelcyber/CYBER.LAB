#!/bin/bash
# Windows Server 2025 Lab Manager

LAB_DIR="/workspaces/CYBER.LAB/lab"
COMPOSE_FILE="docker-compose-windows-2025.yml"

print_header() {
    echo "╔════════════════════════════════════════════════════════════════════════╗"
    echo "║                 CYBER.LAB - WINDOWS SERVER 2025 LAB                    ║"
    echo "║        Domain Controller + Exchange + SharePoint + Honeypot            ║"
    echo "╚════════════════════════════════════════════════════════════════════════╝"
    echo ""
}

print_services() {
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo "WINDOWS LAB SERVICES OVERVIEW"
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
    echo "DOMAIN CONTROLLER (WIN-DC-2025):"
    echo "  ├─ IP Address: 172.28.1.10"
    echo "  ├─ Services: Active Directory, DNS, Kerberos"
    echo "  ├─ LDAP: port 389 (389:389 mapped)"
    echo "  ├─ Kerberos: port 88 (88:88 mapped)"
    echo "  ├─ SMB: port 445 (445:445 mapped)"
    echo "  ├─ RDP: port 3389 (3389:3389 mapped)"
    echo "  └─ Access: mstsc /v:localhost:3389"
    echo ""
    echo "EXCHANGE SERVER 2025 (WIN-EXCH-2025):"
    echo "  ├─ IP Address: 172.28.1.11"
    echo "  ├─ Services: SMTP, IMAP, POP3, HTTP/HTTPS"
    echo "  ├─ SMTP: port 25 (25:25 mapped)"
    echo "  ├─ IMAP: port 143 (143:143 mapped)"
    echo "  ├─ IMAPS: port 993 (993:993 mapped)"
    echo "  ├─ HTTP: port 80 (80:80 mapped)"
    echo "  ├─ HTTPS: port 443 (443:443 mapped)"
    echo "  ├─ RDP: port 3390 (3390:3389 mapped)"
    echo "  ├─ Mailboxes: admin@cyber.lab, exchange@cyber.lab, user@cyber.lab"
    echo "  └─ Access: telnet localhost 25 (SMTP) or Outlook"
    echo ""
    echo "SHAREPOINT/ONEDRIVE (WIN-SP-2025):"
    echo "  ├─ IP Address: 172.28.1.12"
    echo "  ├─ Services: IIS, SharePoint, OneDrive"
    echo "  ├─ HTTP: port 8080 (8080:8080 mapped)"
    echo "  ├─ HTTPS: port 8443 (8443:8443 mapped)"
    echo "  ├─ RDP: port 3391 (3391:3389 mapped)"
    echo "  ├─ Sites: /sites/company, /sites/hr, /sites/finance, /sites/it"
    echo "  └─ Access: http://localhost:8080"
    echo ""
    echo "USER MACHINE (USER-PC-2025):"
    echo "  ├─ IP Address: 172.28.1.20"
    echo "  ├─ OS: Windows 11 Pro (simulated)"
    echo "  ├─ Domain: cyber.lab"
    echo "  ├─ Local Users: user (User2026!) / admin (Admin2026!)"
    echo "  ├─ RDP: port 3392 (3392:3389 mapped)"
    echo "  ├─ Services: Office 365 integration, OneDrive, Outlook Web"
    echo "  └─ Access: mstsc /v:localhost:3392"
    echo ""
    echo "HONEYPOT SERVER (WIN-HONEYPOT):"
    echo "  ├─ IP Address: 172.28.1.30"
    echo "  ├─ External Access: Outside lab network"
    echo "  ├─ Services: Fake databases, fake documents, web portal"
    echo "  ├─ HTTP: port 8000 (8000:8000 mapped)"
    echo "  ├─ HTTPS: port 8443 (8443:8443 mapped)"
    echo "  ├─ RDP: port 3393 (3393:3389 mapped)"
    echo "  ├─ Fake Files: Credentials.txt, DB_Backup.sql, Private_Key.pem"
    echo "  └─ Purpose: Detect and log attacker activities"
    echo ""
    echo "DOMAIN CREDENTIALS:"
    echo "  ├─ Domain: cyber.lab"
    echo "  ├─ Admin Account: LabAdmin"
    echo "  ├─ Admin Password: P@ssw0rd2026!"
    echo "  └─ User Accounts: ITManager, FinanceUser, HRUser, TestUser"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════════════"
    echo ""
}

case "$1" in
    start)
        print_header
        echo "[*] Starting Windows Server 2025 Lab..."
        cd "$LAB_DIR"
        docker-compose -f $COMPOSE_FILE up -d
        
        echo "[+] Lab started!"
        sleep 10
        print_services
        
        echo "[*] Initializing services... (this may take 5-10 minutes)"
        echo "    Domain Controller setup in progress..."
        echo "    Exchange service initialization..."
        echo "    SharePoint site creation..."
        echo ""
        echo "[!] Once all services start, you can connect:"
        echo "    Domain Controller RDP: localhost:3389 (LabAdmin/P@ssw0rd2026!)"
        echo "    Exchange Server RDP: localhost:3390 (LabAdmin/P@ssw0rd2026!)"
        echo "    SharePoint RDP: localhost:3391 (LabAdmin/P@ssw0rd2026!)"
        echo "    User Machine RDP: localhost:3392 (user/User2026!)"
        echo "    Honeypot RDP: localhost:3393 (admin/P@ssw0rd2026!)"
        echo ""
        ;;

    stop)
        echo "[*] Stopping Windows Server 2025 Lab..."
        cd "$LAB_DIR"
        docker-compose -f $COMPOSE_FILE down
        echo "[+] Lab stopped!"
        ;;

    status)
        print_header
        echo "[*] Lab Services Status:"
        cd "$LAB_DIR"
        docker-compose -f $COMPOSE_FILE ps
        echo ""
        ;;

    restart)
        echo "[*] Restarting Windows Server 2025 Lab..."
        cd "$LAB_DIR"
        docker-compose -f $COMPOSE_FILE restart
        echo "[+] Lab restarted!"
        ;;

    logs)
        print_header
        echo "[*] Lab Service Logs (Press Ctrl+C to stop)..."
        cd "$LAB_DIR"
        docker-compose -f $COMPOSE_FILE logs -f --tail=100
        ;;

    info)
        print_header
        print_services
        ;;

    rdp-dc)
        echo "[*] Connecting to Domain Controller via RDP..."
        mstsc /v:localhost:3389 /admin &
        ;;

    rdp-exchange)
        echo "[*] Connecting to Exchange Server via RDP..."
        mstsc /v:localhost:3390 /admin &
        ;;

    rdp-sharepoint)
        echo "[*] Connecting to SharePoint Server via RDP..."
        mstsc /v:localhost:3391 /admin &
        ;;

    rdp-user)
        echo "[*] Connecting to User Machine via RDP..."
        mstsc /v:localhost:3392 &
        ;;

    rdp-honeypot)
        echo "[*] Connecting to Honeypot Server via RDP..."
        mstsc /v:localhost:3393 /admin &
        ;;

    ldap-query)
        echo "[*] Querying Active Directory via LDAP..."
        cat << 'EOF'
# LDAP Query Examples:

# List all users:
ldapsearch -H ldap://localhost:389 -D "cn=admin,dc=cyber,dc=lab" -w Admin123456 -b "dc=cyber,dc=lab" "objectClass=user"

# List all groups:
ldapsearch -H ldap://localhost:389 -D "cn=admin,dc=cyber,dc=lab" -w Admin123456 -b "dc=cyber,dc=lab" "objectClass=group"

# Find specific user:
ldapsearch -H ldap://localhost:389 -D "cn=admin,dc=cyber,dc=lab" -w Admin123456 -b "dc=cyber,dc=lab" "sAMAccountName=LabAdmin"

# Using ldapsearch on Linux:
ldapsearch -x -H ldap://localhost:389 -b "dc=cyber,dc=lab"
EOF
        ;;

    smtp-test)
        echo "[*] Testing SMTP connection..."
        telnet localhost 25
        ;;

    imap-test)
        echo "[*] Testing IMAP connection..."
        echo "# Connect to IMAP server and test:"
        echo "telnet localhost 143"
        ;;

    clean)
        echo "╔════════════════════════════════════════════════════════════════════════╗"
        echo "║                         ⚠️  WARNING  ⚠️                                  ║"
        echo "║  This will DELETE all Windows Server 2025 lab data permanently!         ║"
        echo "╚════════════════════════════════════════════════════════════════════════╝"
        read -p "Type 'YES' to confirm deletion: " confirm
        if [ "$confirm" = "YES" ]; then
            echo "[*] Removing all volumes and containers..."
            cd "$LAB_DIR"
            docker-compose -f $COMPOSE_FILE down -v
            echo "[+] Lab data removed!"
        else
            echo "[-] Operation cancelled"
        fi
        ;;

    *)
        print_header
        echo "Usage: $0 {start|stop|restart|status|logs|info|rdp-*|ldap-query|smtp-test|clean}"
        echo ""
        echo "Start/Stop Commands:"
        echo "  start           - Start all Windows 2025 lab services"
        echo "  stop            - Stop all services"
        echo "  restart         - Restart all services"
        echo "  status          - Show current status"
        echo "  logs            - Follow service logs"
        echo ""
        echo "RDP Connection Commands:"
        echo "  rdp-dc          - Connect to Domain Controller"
        echo "  rdp-exchange    - Connect to Exchange Server"
        echo "  rdp-sharepoint  - Connect to SharePoint Server"
        echo "  rdp-user        - Connect to User Machine"
        echo "  rdp-honeypot    - Connect to Honeypot"
        echo ""
        echo "Testing Commands:"
        echo "  ldap-query      - LDAP query examples"
        echo "  smtp-test       - Test SMTP on Exchange"
        echo "  imap-test       - Test IMAP on Exchange"
        echo ""
        echo "Maintenance:"
        echo "  info            - Show detailed service information"
        echo "  clean           - Remove all lab data (DESTRUCTIVE)"
        echo ""
        ;;
esac
