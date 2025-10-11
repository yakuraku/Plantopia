# Quick Manual Fix for Production Server

## Current Situation
You have `httpx==0.28.1` installed, but need `httpx 0.24.x or 0.25.x` for compatibility.

---

## 🚀 Manual Fix (Run This Now on Server)

```bash
# 1. Pull latest code
cd /opt/plantopia/Plantopia
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate

# 3. FORCE downgrade httpx to compatible version
pip uninstall -y httpx
pip install "httpx>=0.24.1,<0.26.0"

# 4. Verify httpx version (should be 0.24.x or 0.25.x)
pip show httpx | grep Version
# Expected: Version: 0.24.1 or 0.25.x (NOT 0.28.x)

# 5. Reinstall supabase to ensure compatibility
pip install --upgrade --force-reinstall supabase

# 6. Verify no conflicts
pip check
# Expected: No broken requirements found.

# 7. Run database migrations
alembic upgrade head

# 8. Restart application
sudo supervisorctl restart plantopia

# 9. Check service status
sudo supervisorctl status plantopia

# 10. Test health endpoint
curl http://localhost:8000/
# Expected: {"message":"Plantopia API is running"}
```

---

## 🔍 Verification Steps

After running the above, verify the versions:

```bash
pip list | grep -E "supabase|httpx|PyJWT|gotrue|supafunc"
```

**Expected Output:**
```
httpx                        0.24.1 (or 0.25.x - NOT 0.28.x) ✅
PyJWT                        2.10.1 or higher ✅
supabase                     2.22.0 or higher ✅
supabase-auth                2.x.x ✅
gotrue                       Compatible version ✅
supafunc                     Compatible version ✅
```

---

## 🎯 What This Does

1. **Uninstall httpx** - Removes the incompatible 0.28.1 version
2. **Install httpx with constraint** - Forces 0.24.x or 0.25.x range
3. **Force reinstall supabase** - Ensures all sub-dependencies align
4. **Verify with pip check** - Confirms no conflicts
5. **Run migrations** - Creates new database tables for Iteration 3
6. **Restart app** - Applies all changes

---

## 🚨 If You Still Get Conflicts

Run the full cleanup script:

```bash
cd /opt/plantopia/Plantopia
chmod +x fix_dependencies.sh
./fix_dependencies.sh
```

This will:
- Uninstall ALL supabase packages
- Clear pip cache
- Reinstall everything in correct order
- Install httpx BEFORE supabase (order matters!)

---

## ✅ Success Indicators

You'll know it's working when:
- ✅ `pip check` shows no errors
- ✅ `httpx` version is 0.24.x or 0.25.x (NOT 0.28.x)
- ✅ `supervisorctl status plantopia` shows RUNNING
- ✅ `curl http://localhost:8000/` returns JSON response
- ✅ Swagger UI loads at `http://YOUR_IP/docs`

---

## 📋 Next Steps After Fix

1. **Test Plant Tracking Endpoints:**
   ```bash
   curl -X GET http://localhost:8000/docs
   # Look for /plant-tracking/* endpoints
   ```

2. **Test Chat Endpoints:**
   ```bash
   curl -X GET http://localhost:8000/docs
   # Look for /chat/* endpoints
   ```

3. **Verify Database Tables:**
   ```bash
   alembic current
   # Should show: b9d2f7e8a3c1 (head)
   ```

---

## 🔄 Future Deployments (Automated!)

**From now on**, when you push to `main`:

1. GitHub Actions will automatically:
   - ✅ Pull latest code
   - ✅ Run `fix_dependencies.sh` (ensures clean install)
   - ✅ Run `alembic upgrade head` (auto-migrations)
   - ✅ Restart application
   - ✅ Run health checks

2. You **DON'T need to SSH** into the server anymore!

3. Just push to main and monitor GitHub Actions:
   ```
   https://github.com/yakuraku/Plantopia/actions
   ```

---

## 🆘 Troubleshooting

**If deployment fails:**

1. Check GitHub Actions logs
2. SSH into server and run:
   ```bash
   sudo supervisorctl tail -100 plantopia
   journalctl -u plantopia -n 100
   ```
3. Check database connection:
   ```bash
   psql $DATABASE_URL -c "SELECT version();"
   ```

**If migrations fail:**

```bash
alembic current
alembic history
alembic upgrade head --sql  # Show SQL without executing
```

**If httpx conflict persists:**

```bash
pip freeze | grep httpx
pip uninstall -y httpx
pip cache purge
pip install "httpx==0.24.1"  # Force exact version
```
