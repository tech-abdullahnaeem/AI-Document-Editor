#!/bin/bash
# Deploy Document Editor API to DigitalOcean

DROPLET_IP="161.35.235.101"
PROJECT_NAME="document-editor-api"

echo "🚀 Deploying to DigitalOcean Droplet: $DROPLET_IP"
echo ""

# Step 1: Create project directory on droplet
echo "📁 Creating project directory..."
ssh root@$DROPLET_IP "mkdir -p /root/$PROJECT_NAME"

# Step 2: Copy project files (excluding venv, caches, etc.)
echo "📤 Uploading project files..."
rsync -avz --progress \
  --exclude='venv' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='uploads/' \
  --exclude='downloads/' \
  --exclude='editing output*/' \
  --exclude='edit output*/' \
  --exclude='*.pdf' \
  --exclude='examples/' \
  --exclude='Rag latex fixer/' \
  --exclude='sample equations pdf/' \
  . root@$DROPLET_IP:/root/$PROJECT_NAME/

# Step 3: Run deployment script
echo ""
echo "🔧 Running deployment script on droplet..."
ssh root@$DROPLET_IP "cd /root/$PROJECT_NAME && chmod +x deploy.sh && ./deploy.sh"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "1. SSH into your droplet: ssh root@$DROPLET_IP"
echo "2. Edit .env file: nano /home/appuser/document-editor-api/.env"
echo "3. Add your GEMINI_API_KEY"
echo "4. Restart service: systemctl restart document-editor-api"
echo "5. Access API: http://$DROPLET_IP/docs"

