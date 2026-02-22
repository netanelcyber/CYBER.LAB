#!/bin/bash
# Enterprise Lab Control Script

LAB_DIR="/workspaces/CYBER.LAB/lab"
DOCKER_COMPOSE="docker-compose-enterprise.yml"

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                  CYBER.LAB - ENTERPRISE LAB MANAGER                  ║"
echo "║           Active Directory + Exchange + O365 + Vulnerable Lab        ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

case "$1" in
  start)
    echo "[*] Starting Enterprise Lab..."
    cd "$LAB_DIR"
    docker-compose -f $DOCKER_COMPOSE up -d
    echo "[+] Lab started!"
    sleep 5
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo "LAB SERVICES & ACCESS POINTS"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Active Directory & Domain Services:"
    echo "  ├─ Samba DC (LDAP): ldap://172.28.0.2:389 (bind: cn=admin,dc=cyber,dc=lab)"
    echo "  ├─ OpenLDAP: ldap://172.28.0.3:389"
    echo "  └─ LDAP Admin UI: http://localhost:8080 (admin/admin123456)"
    echo ""
    echo "Exchange & Email Services:"
    echo "  ├─ SMTP: localhost:25"
    echo "  ├─ IMAP: localhost:143"
    echo "  ├─ IMAPS: localhost:993"
    echo "  └─ Account: admin@cyber.lab / P@ssw0rd2026!"
    echo ""
    echo "O365 & Cloud Services:"
    echo "  ├─ O365 API Simulator: http://localhost:8090"
    echo "  │  └─ Login: admin@cyber.lab / P@ssw0rd2026!"
    echo "  └─ SharePoint/OneDrive: http://localhost:8091"
    echo ""
    echo "Web Applications:"
    echo "  ├─ Drupal 7 (172.28.0.22:8001): http://localhost:8001"
    echo "  └─ WordPress (172.28.0.24:8002): http://localhost:8002"
    echo ""
    echo "UNPATCHED/VULNERABLE MACHINES (External Access):"
    echo "  ├─ Unpatched Windows (RDP): localhost:3389"
    echo "  │  └─ Credentials: admin / P@ssw0rd2026!"
    echo "  ├─ Unpatched Linux (SSH): localhost:22"
    echo "  │  ├─ User: testuser / password"
    echo "  │  ├─ Admin: admin / P@ssw0rd2026!"
    echo "  │  ├─ Vulnerable OpenSSH 7.2"
    echo "  │  ├─ Vulnerable Apache 2.4.18"
    echo "  │  ├─ Vulnerable PHP 5.6"
    echo "  │  └─ HTTP: http://localhost:8444 (with RCE vulnerabilities!)"
    echo ""
    echo "Monitoring & Analysis:"
    echo "  ├─ Elasticsearch: http://localhost:9200"
    echo "  └─ Kibana: http://localhost:5601"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    ;;

  stop)
    echo "[*] Stopping Enterprise Lab..."
    cd "$LAB_DIR"
    docker-compose -f $DOCKER_COMPOSE down
    echo "[+] Lab stopped!"
    ;;

  status)
    echo "[*] Lab Services Status:"
    cd "$LAB_DIR"
    docker-compose -f $DOCKER_COMPOSE ps
    echo ""
    ;;

  logs)
    echo "[*] Showing logs (use Ctrl+C to stop)..."
    cd "$LAB_DIR"
    docker-compose -f $DOCKER_COMPOSE logs -f
    ;;

  clean)
    echo "[!] WARNING: This will delete all lab data!"
    read -p "Continue? (y/N): " confirm
    if [ "$confirm" = "y" ]; then
      cd "$LAB_DIR"
      docker-compose -f $DOCKER_COMPOSE down -v
      echo "[+] Lab cleaned!"
    fi
    ;;

  *)
    echo "Usage: $0 {start|stop|status|logs|clean}"
    echo ""
    echo "Commands:"
    echo "  start   - Start all lab services"
    echo "  stop    - Stop all lab services"
    echo "  status  - Show service status"
    echo "  logs    - Follow service logs"
    echo "  clean   - Stop and remove all data"
    echo ""
    ;;
esac
