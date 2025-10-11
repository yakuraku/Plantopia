#!/bin/bash
# Dependency Fix Script for Plantopia
# Resolves conflicts between supabase, gotrue, supafunc, and httpx

set -e

echo "🔧 Starting dependency cleanup and reinstall..."

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Please create it first:"
    echo "   python -m venv venv"
    exit 1
fi

echo ""
echo "📋 Step 1: Clearing pip cache..."
pip cache purge

echo ""
echo "📋 Step 2: Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

echo ""
echo "📋 Step 3: Installing all dependencies from requirements.txt..."
# Simple approach: just install from requirements.txt
# This uses the known-working versions
pip install -r requirements.txt

echo ""
echo "📋 Step 4: Verifying installation..."
pip check

echo ""
echo "📊 Step 5: Showing installed versions of critical packages..."
echo "----------------------------------------"
pip list | grep -E "supabase|httpx|PyJWT|google-generativeai|Pillow"
echo "----------------------------------------"

echo ""
echo "✅ Dependency installation complete!"
echo ""
echo "🔍 Next steps:"
echo "  1. Run database migrations: alembic upgrade head"
echo "  2. Restart application: sudo supervisorctl restart plantopia"
echo "  3. Test health endpoint: curl http://localhost:8000/"
