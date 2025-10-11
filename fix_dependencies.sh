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
echo "📋 Step 1: Uninstalling conflicting packages..."
pip uninstall -y supabase gotrue supafunc httpx supabase-auth storage3 realtime postgrest-py 2>/dev/null || true

echo ""
echo "📋 Step 2: Clearing pip cache..."
pip cache purge

echo ""
echo "📋 Step 3: Upgrading pip and setuptools..."
pip install --upgrade pip setuptools wheel

echo ""
echo "📋 Step 4: Installing core dependencies first..."
# Install non-supabase dependencies first
pip install pandas python-dateutil fastapi uvicorn python-multipart python-dotenv requests

echo ""
echo "📋 Step 5: Installing database dependencies..."
pip install sqlalchemy==2.0.23 asyncpg==0.29.0 alembic==1.13.1 psycopg2-binary==2.9.9 greenlet==3.0.3

echo ""
echo "📋 Step 6: Installing auth dependencies with compatible versions..."
pip install "PyJWT>=2.10.1" "python-jose[cryptography]==3.3.0"

echo ""
echo "📋 Step 7: Installing httpx with version constraint FIRST (before supabase)..."
pip install "httpx>=0.24.1,<0.26.0"

echo ""
echo "📋 Step 8: Installing supabase with all dependencies (will use existing httpx)..."
pip install "supabase>=2.22.0"

echo ""
echo "📋 Step 9: Installing remaining dependencies..."
pip install aiohttp==3.9.1 google-auth==2.28.0 pytest==7.4.0 pytest-asyncio==0.21.0 google-generativeai==0.8.0

echo ""
echo "📋 Step 10: Verifying installation..."
pip check

echo ""
echo "📊 Step 11: Showing installed versions of critical packages..."
echo "----------------------------------------"
pip list | grep -E "supabase|httpx|PyJWT|gotrue|supafunc|storage3"
echo "----------------------------------------"

echo ""
echo "✅ Dependency installation complete!"
echo ""
echo "🔍 Next steps:"
echo "  1. Run database migrations: alembic upgrade head"
echo "  2. Restart application: sudo systemctl restart plantopia"
echo "  3. Test health endpoint: curl http://localhost:8000/"
