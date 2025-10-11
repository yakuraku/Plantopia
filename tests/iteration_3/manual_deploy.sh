#!/bin/bash
# Manual Deployment Script - Run this on VM if GitHub Actions didn't deploy

set -e

echo "🚀 Starting manual deployment..."

# Navigate to project directory
cd /opt/plantopia/Plantopia

echo "📥 Pulling latest code..."
git fetch origin
git reset --hard origin/main

echo "🐍 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing any new dependencies..."
pip install -q -r requirements.txt

echo "🗄️  Running database migrations..."
alembic upgrade head

echo "🔄 Restarting application..."
sudo supervisorctl restart plantopia

echo "⏳ Waiting for application to start (30 seconds)..."
sleep 30

echo "🔍 Checking application status..."
sudo supervisorctl status plantopia

echo "✅ Deployment complete!"
echo ""
echo "📋 Current git status:"
git log --oneline -3

echo ""
echo "🧪 Now you can run the tests:"
echo "cd tests/iteration_3"
echo "python realistic_user_scenarios_test.py http://localhost:8000/api/v1"
