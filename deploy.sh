#!/bin/bash

# ============================================================================
# DOCUMENT EDITOR API - AUTOMATED DEPLOYMENT SCRIPT
# For DigitalOcean Ubuntu 22.04 LTS / 24.04 LTS
# Usage: curl -sSL https://your-repo/deploy.sh | bash
# Or: chmod +x deploy.sh && ./deploy.sh
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="document-editor-api"
APP_USER="appuser"
APP_DIR="/home/appuser/document-editor-api"
REPO_URL="https://github.com/yourusername/document-editor-api.git"  # Update this
LOG_DIR="/var/log/document-editor-api"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

update_system() {
    log_info "Updating system packages..."
    apt-get update > /dev/null 2>&1
    apt-get upgrade -y > /dev/null 2>&1
    log_success "System packages updated"
}

install_dependencies() {
    log_info "Installing system dependencies..."
    
    # Check if already installed
    if command -v python3 &> /dev/null && dpkg -l | grep -q texlive-full; then
        log_warning "Dependencies appear already installed, skipping..."
        return
    fi
    
    apt-get install -y \
        build-essential \
        curl \
        wget \
        git \
        python3-pip \
        python3-venv \
        python3-dev \
        texlive-full \
        texlive-xetex \
        texlive-fonts-recommended \
        texlive-fonts-extra \
        imagemagick \
        ghostscript \
        poppler-utils \
        tesseract-ocr \
        libtesseract-dev \
        nginx \
        certbot \
        python3-certbot-nginx \
        > /dev/null 2>&1
    
    log_success "System dependencies installed"
}

create_app_user() {
    log_info "Setting up application user..."
    
    if id "$APP_USER" &>/dev/null; then
        log_warning "User $APP_USER already exists, skipping..."
        return
    fi
    
    useradd -m -s /bin/bash "$APP_USER"
    usermod -aG sudo "$APP_USER"
    log_success "Application user created"
}

clone_repository() {
    log_info "Cloning repository..."
    
    if [ -d "$APP_DIR" ]; then
        log_warning "Directory $APP_DIR already exists, updating..."
        cd "$APP_DIR"
        sudo -u "$APP_USER" git pull
    else
        sudo -u "$APP_USER" git clone "$REPO_URL" "$APP_DIR"
    fi
    
    log_success "Repository cloned/updated"
}

setup_venv() {
    log_info "Setting up Python virtual environment..."
    
    cd "$APP_DIR"
    
    if [ ! -d "venv" ]; then
        sudo -u "$APP_USER" python3 -m venv venv
    fi
    
    # Install requirements
    sudo -u "$APP_USER" bash -c "source venv/bin/activate && pip install --upgrade pip setuptools wheel > /dev/null 2>&1"
    sudo -u "$APP_USER" bash -c "source venv/bin/activate && pip install -r requirements.txt > /dev/null 2>&1"
    
    log_success "Virtual environment setup complete"
}

setup_env_file() {
    log_info "Setting up environment file..."
    
    if [ ! -f "$APP_DIR/.env" ]; then
        cp "$APP_DIR/.env.example" "$APP_DIR/.env"
        log_warning "Please edit $APP_DIR/.env with your credentials:"
        echo ""
        echo "Required:"
        echo "  - GEMINI_API_KEY: Get from https://aistudio.google.com/app/apikeys"
        echo "  - FASTAPI_API_KEY: Generate a strong secret key"
        echo ""
        return
    fi
    
    log_success "Environment file exists"
}

create_directories() {
    log_info "Creating required directories..."
    
    mkdir -p "$LOG_DIR"
    mkdir -p /var/lib/document-editor/{uploads,downloads,temp}
    
    chown -R "$APP_USER:$APP_USER" "$LOG_DIR"
    chown -R "$APP_USER:$APP_USER" /var/lib/document-editor
    chmod -R 755 /var/lib/document-editor
    
    log_success "Directories created"
}

setup_systemd_service() {
    log_info "Setting up systemd service..."
    
    cat > /etc/systemd/system/document-editor-api.service << 'EOF'
[Unit]
Description=Document Editing API Service
After=network.target

[Service]
Type=notify
User=appuser
WorkingDirectory=/home/appuser/document-editor-api/fastapi_backend
Environment="PATH=/home/appuser/document-editor-api/venv/bin"
EnvironmentFile=/home/appuser/document-editor-api/.env
ExecStart=/home/appuser/document-editor-api/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --access-logfile /var/log/document-editor-api/access.log \
    --error-logfile /var/log/document-editor-api/error.log \
    main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable document-editor-api
    
    log_success "Systemd service created and enabled"
}

setup_nginx() {
    log_info "Setting up Nginx reverse proxy..."
    
    # Backup existing default config
    if [ -f /etc/nginx/sites-enabled/default ]; then
        mv /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.bak
    fi
    
    cat > /etc/nginx/sites-available/document-editor-api << 'EOF'
upstream document_editor {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://document_editor;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
EOF

    if [ ! -L /etc/nginx/sites-enabled/document-editor-api ]; then
        ln -s /etc/nginx/sites-available/document-editor-api /etc/nginx/sites-enabled/
    fi
    
    nginx -t > /dev/null 2>&1 && systemctl restart nginx
    
    log_success "Nginx configured"
}

start_services() {
    log_info "Starting services..."
    
    systemctl start document-editor-api
    systemctl restart nginx
    
    sleep 2
    
    if systemctl is-active --quiet document-editor-api; then
        log_success "Document Editor API service is running"
    else
        log_error "Failed to start Document Editor API service"
        systemctl status document-editor-api
        exit 1
    fi
}

print_status() {
    log_info "Checking service status..."
    echo ""
    systemctl status document-editor-api --no-pager | head -20
    echo ""
}

print_next_steps() {
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
    echo -e "${BLUE}============================================================${NC}"
    echo ""
    echo "📝 NEXT STEPS:"
    echo ""
    echo "1. Edit environment file with your credentials:"
    echo "   nano $APP_DIR/.env"
    echo ""
    echo "2. Required credentials:"
    echo "   - GEMINI_API_KEY: https://aistudio.google.com/app/apikeys"
    echo "   - FASTAPI_API_KEY: Generate a strong secret key"
    echo ""
    echo "3. After updating .env, restart the service:"
    echo "   systemctl restart document-editor-api"
    echo ""
    echo "4. Check logs:"
    echo "   journalctl -u document-editor-api -f"
    echo ""
    echo "5. Test the API:"
    echo "   curl http://localhost/health"
    echo "   curl http://localhost/docs"
    echo ""
    echo "6. Setup SSL (optional but recommended):"
    echo "   certbot certonly --nginx -d yourdomain.com"
    echo ""
    echo "📊 Important paths:"
    echo "   - Application: $APP_DIR"
    echo "   - Logs: $LOG_DIR"
    echo "   - Config: $APP_DIR/.env"
    echo "   - Uploads: /var/lib/document-editor/uploads"
    echo "   - Downloads: /var/lib/document-editor/downloads"
    echo ""
    echo -e "${BLUE}============================================================${NC}"
    echo ""
}

main() {
    log_info "Starting Document Editor API deployment..."
    echo ""
    
    check_root
    update_system
    install_dependencies
    create_app_user
    clone_repository
    setup_venv
    create_directories
    setup_env_file
    setup_systemd_service
    setup_nginx
    start_services
    print_status
    print_next_steps
    
    log_success "Deployment script completed successfully!"
}

# Run main function
main "$@"
