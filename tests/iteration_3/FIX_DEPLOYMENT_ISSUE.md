# 🔴 Deployment Issue - Quick Fix

## Problem

The VM is running **old code**. The GitHub Actions deployment either:
1. Didn't run yet (check: https://github.com/yakuraku/Plantopia/actions)
2. Failed silently
3. The VM didn't pull the latest changes

## Evidence

Test errors show:
- ❌ `'StartTrackingRequest' object has no attribute 'user_id'` - OLD CODE
- ❌ Favorites returns `'Not authenticated'` - OLD CODE (auth not removed)
- ❌ Guides endpoint 404 - NEW ENDPOINTS NOT DEPLOYED

## ✅ Quick Fix (Run on VM)

### Option 1: Manual Deployment Script

```bash
# On VM, in project directory
cd /opt/plantopia/Plantopia

# Make script executable
chmod +x tests/iteration_3/manual_deploy.sh

# Run manual deployment
./tests/iteration_3/manual_deploy.sh
```

This will:
1. Pull latest code from GitHub
2. Run database migration
3. Restart the application

### Option 2: Manual Steps

If script doesn't work, run these commands manually:

```bash
# 1. Navigate to project
cd /opt/plantopia/Plantopia

# 2. Pull latest code
git fetch origin
git reset --hard origin/main

# 3. Check you have the right commit
git log --oneline -3
# Should show:
# 56008ab docs: add quick start guide for testing
# c95066d test: add comprehensive realistic user scenarios test suite
# 5590d48 feat: migrate to email-based authentication and add plant guide favorites

# 4. Activate virtual environment
source venv/bin/activate

# 5. Run database migration
alembic upgrade head

# 6. Restart application
sudo supervisorctl restart plantopia

# 7. Wait for restart
sleep 30

# 8. Check status
sudo supervisorctl status plantopia
```

### Option 3: Check GitHub Actions

```bash
# Check if deployment workflow is still running
# Go to: https://github.com/yakuraku/Plantopia/actions

# If it's still running, wait for it to complete
# If it failed, check the logs
```

## Verification

After running the fix, verify the code is updated:

```bash
# Check git commit
cd /opt/plantopia/Plantopia
git log --oneline -1
# Should show: 56008ab docs: add quick start guide for testing

# Check if new endpoints exist
curl http://localhost:8000/api/v1/guides/categories
# Should return JSON with categories, NOT 404

# Check if old auth is removed
curl -X GET "http://localhost:8000/api/v1/favorites?email=test@example.com"
# Should return empty array or 404, NOT 403 'Not authenticated'
```

## Then Re-run Tests

```bash
cd /opt/plantopia/Plantopia/tests/iteration_3

# Fix permissions on reports folder
chmod 777 reports/

# Run tests again
python realistic_user_scenarios_test.py http://localhost:8000/api/v1
```

## Expected After Fix

Tests should start working:
- ✅ Email-based authentication working
- ✅ No more `user_id` errors
- ✅ Guides endpoint found (200, not 404)
- ✅ Favorites no auth required (not 403)

---

## Root Cause Analysis

The issue is that **GitHub Actions deployment workflow ran but the VM code wasn't updated**. This can happen if:

1. **Git pull failed** - Permissions or local changes
2. **Supervisor didn't restart** - Service not reloaded
3. **Migration didn't run** - Database out of sync
4. **Cache issue** - Old code cached

The manual deployment script fixes all of these.

---

**Run the manual deployment script on VM, then re-run tests!**
