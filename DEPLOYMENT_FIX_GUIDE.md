# Deployment Fix Guide - Iteration 3

## Critical Issues Identified

### Issue 1: Git Lock File (CRITICAL)
**Error:**
```
fatal: Unable to create '/opt/plantopia/Plantopia/.git/index.lock': File exists.
```

**Cause:** A previous git process crashed or was interrupted, leaving a stale lock file.

**Fix:**
```bash
# SSH into production server
cd /opt/plantopia/Plantopia

# Remove the stale lock file
rm -f .git/index.lock

# Clean up any other git locks
rm -f .git/refs/heads/*.lock
rm -f .git/refs/remotes/origin/*.lock

# Verify git is working
git status
```

---

### Issue 2: Git Branch Reference Locks
**Error:**
```
error: cannot lock ref 'refs/remotes/origin/dev-parth'
error: cannot lock ref 'refs/remotes/origin/dev-yash'
```

**Cause:** Corrupted remote branch references.

**Fix:**
```bash
# Clean up remote branch references
cd /opt/plantopia/Plantopia

# Remove problematic remote refs
rm -f .git/refs/remotes/origin/dev-parth
rm -f .git/refs/remotes/origin/dev-yash

# Fetch fresh remote references
git fetch --prune origin

# Verify remotes are clean
git branch -r
```

---

### Issue 3: Python Dependency Conflicts
**Error:**
```
supabase-auth 2.12.3 requires httpx[http2]<0.29,>=0.26, but you have httpx 0.24.1
supabase-auth 2.12.3 requires pyjwt<3.0.0,>=2.10.1, but you have pyjwt 2.8.0
```

**Cause:** Outdated dependency versions in requirements.txt.

**Fix:** ✅ Already fixed in latest commit
- Updated `httpx==0.24.1` → `httpx==0.27.0`
- Updated `PyJWT==2.8.0` → `PyJWT==2.10.1`

**Action Required:**
```bash
# After pulling latest code, reinstall dependencies
cd /opt/plantopia/Plantopia
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

### Issue 4: Application Startup Failure
**Error:**
```
❌ Application failed to start
```

**Cause:** Likely due to:
1. Missing database migrations
2. Dependency conflicts (fixed above)
3. Missing environment variables

**Fix:**
```bash
# 1. Check application logs for specific error
journalctl -u plantopia -n 100 --no-pager

# 2. Run database migrations
cd /opt/plantopia/Plantopia
source venv/bin/activate
alembic upgrade head

# 3. Verify environment variables
cat .env | grep -E "DATABASE_URL|GEMINI_API_KEY|SUPABASE"

# 4. Test application manually
uvicorn app.main:app --host 0.0.0.0 --port 8000
# Press Ctrl+C after verifying it starts

# 5. Restart service
sudo systemctl restart plantopia
sudo systemctl status plantopia
```

---

## Complete Fix Procedure (Step-by-Step)

### Step 1: Fix Git Issues
```bash
# SSH into production server
ssh user@your-production-server

# Navigate to project directory
cd /opt/plantopia/Plantopia

# Remove all git lock files
rm -f .git/index.lock
rm -f .git/refs/heads/*.lock
rm -f .git/refs/remotes/origin/*.lock

# Clean up corrupted remote refs
rm -f .git/refs/remotes/origin/dev-parth
rm -f .git/refs/remotes/origin/dev-yash

# Verify git is working
git status
```

**Expected Output:**
```
On branch main
Your branch is behind 'origin/main' by X commits
nothing to commit, working tree clean
```

---

### Step 2: Pull Latest Code
```bash
# Pull latest changes (including dependency fixes)
git fetch --prune origin
git pull origin main

# Verify you're on latest commit
git log -1 --oneline
# Should show: "Fix dependency conflicts for deployment"
```

---

### Step 3: Update Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip

# Install updated dependencies
pip install --upgrade -r requirements.txt

# Verify no conflicts
pip check
# Should show: "No broken requirements found."
```

---

### Step 4: Run Database Migrations
```bash
# Check current migration status
alembic current

# Run pending migrations
alembic upgrade head

# Verify migrations applied
alembic current
# Should show: b9d2f7e8a3c1 (head)

# Verify new tables exist
psql $DATABASE_URL -c "\dt" | grep -E "user_plant_chats|chat_messages"
```

**Expected Output:**
```
 public | user_plant_chats         | table | plantopia_user
 public | chat_messages            | table | plantopia_user
```

---

### Step 5: Test Application Manually
```bash
# Test startup manually first
uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal, test health endpoint
curl http://localhost:8000/

# Expected: {"message":"Plantopia API is running"}

# Press Ctrl+C to stop manual server
```

---

### Step 6: Restart Production Service
```bash
# Restart the systemd service
sudo systemctl restart plantopia

# Check service status
sudo systemctl status plantopia

# Verify it's running
curl http://localhost:8000/
```

**Expected Status:**
```
● plantopia.service - Plantopia FastAPI Application
   Loaded: loaded
   Active: active (running)
```

---

### Step 7: Verify All Endpoints
```bash
# Test Swagger UI
curl http://your-domain.com/docs

# Test plant tracking endpoint
curl -X POST http://localhost:8000/plant-tracking/start \
  -H "Content-Type: application/json" \
  -d '{
    "user_data": {
      "email": "test@example.com",
      "name": "Test User",
      "suburb_id": 1
    },
    "plant_id": 1,
    "plant_nickname": "My Tomato",
    "start_date": "2025-10-11"
  }'

# Test chat endpoint
curl -X POST http://localhost:8000/chat/general/start \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'
```

---

## Troubleshooting Common Issues

### If migrations fail:
```bash
# Check database connection
psql $DATABASE_URL -c "SELECT version();"

# Check alembic version table
psql $DATABASE_URL -c "SELECT * FROM alembic_version;"

# If stuck, downgrade and re-upgrade
alembic downgrade -1
alembic upgrade head
```

### If dependency conflicts persist:
```bash
# Clear pip cache
pip cache purge

# Reinstall from scratch
pip uninstall -y -r requirements.txt
pip install -r requirements.txt
```

### If application still won't start:
```bash
# Check detailed logs
journalctl -u plantopia -n 200 --no-pager

# Check for Python errors
tail -f /var/log/plantopia/error.log

# Test imports manually
python -c "from app.main import app; print('✅ App imports successfully')"
```

---

## Verification Checklist

After completing all steps, verify:

- [ ] Git status is clean (no lock files)
- [ ] Latest commit is pulled (bb8dc9b or newer)
- [ ] No pip dependency conflicts (`pip check`)
- [ ] Alembic shows head migration (b9d2f7e8a3c1)
- [ ] New database tables exist (5 tables total)
- [ ] Application starts without errors
- [ ] Swagger UI loads at /docs
- [ ] Health endpoint returns 200 OK
- [ ] At least one plant tracking endpoint works
- [ ] At least one chat endpoint works

---

## Quick Reference Commands

```bash
# Full fix in one script (copy-paste friendly)
cd /opt/plantopia/Plantopia && \
rm -f .git/index.lock .git/refs/heads/*.lock .git/refs/remotes/origin/*.lock && \
rm -f .git/refs/remotes/origin/dev-parth .git/refs/remotes/origin/dev-yash && \
git fetch --prune origin && \
git pull origin main && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install --upgrade -r requirements.txt && \
alembic upgrade head && \
sudo systemctl restart plantopia && \
sudo systemctl status plantopia
```

---

## Contact for Issues

If problems persist after following this guide:
1. Check application logs: `journalctl -u plantopia -n 200`
2. Check database logs: `psql $DATABASE_URL -c "SELECT * FROM alembic_version;"`
3. Review this guide's troubleshooting section
4. Share specific error messages for further assistance
