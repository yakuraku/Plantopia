# Fix Git Permissions Issue

## Problem
```
fatal: detected dubious ownership in repository at '/opt/plantopia/Plantopia'
```

This happens when the Git repository is owned by a different user than the one running git commands.

## ✅ Quick Fix

Run these commands on your VM:

```bash
# Option 1: Add safe directory (recommended)
git config --global --add safe.directory /opt/plantopia/Plantopia

# Then try again
git fetch origin
git reset --hard origin/main
```

**OR**

```bash
# Option 2: Fix ownership (if you have sudo)
sudo chown -R $(whoami):$(whoami) /opt/plantopia/Plantopia

# Then try git commands
git fetch origin
git reset --hard origin/main
```

## After Fixing Permissions

Continue with deployment:

```bash
# Check you're on the right commit
git log --oneline -1
# Should show: 44f8b4a or later

# Activate venv
source venv/bin/activate

# Run migration
alembic upgrade head

# Restart app
sudo supervisorctl restart plantopia

# Wait
sleep 30

# Verify
sudo supervisorctl status plantopia
curl http://localhost:8000/api/v1/guides/categories
```

## Then Re-run Tests

```bash
cd tests/iteration_3
sudo chmod 777 reports/
python realistic_user_scenarios_test.py http://localhost:8000/api/v1
```
