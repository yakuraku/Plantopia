# GCP Deployment Guide - Running Alembic Migrations

## Overview
This guide explains how to run database migrations on your GCP server for the Plantopia project.

---

## Prerequisites

Before running migrations, ensure you have:
- SSH access to your GCP VM
- The GCP VM IP address
- Your SSH key or password
- Database credentials (should already be configured on the server)

---

## Option 1: SSH Directly and Run Migration (Recommended)

### Step 1: Connect to GCP Server

```bash
# Replace with your actual GCP VM IP
ssh your-username@YOUR_GCP_VM_IP
```

**Example:**
```bash
ssh yash@34.116.xxx.xxx
```

### Step 2: Navigate to Project Directory

```bash
cd /opt/plantopia/Plantopia
```

### Step 3: Activate Python Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### Step 4: Check Current Migration Status

```bash
# See which migrations have been applied
alembic current

# See all available migrations
alembic history
```

### Step 5: Run the Migrations

```bash
# Run all pending migrations (recommended)
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade a8f3e4b1c5d2 -> b9d2f7e8a3c1, Add chat tables for AI chat feature (Iteration 3 - Session 3)
```

### Step 6: Verify Migration Success

```bash
# Check current migration version
alembic current

# Should show: b9d2f7e8a3c1 (head)
```

### Step 7: Verify Tables Were Created

```bash
# Connect to PostgreSQL database
psql -U your_db_user -d plantopia_db

# List all tables (should see user_plant_chats and chat_messages)
\dt

# Check the new chat tables
\d user_plant_chats
\d chat_messages

# Exit PostgreSQL
\q
```

### Step 8: Restart the Application

```bash
# Exit virtual environment
deactivate

# Restart application with supervisor
sudo supervisorctl restart plantopia

# Check application status
sudo supervisorctl status plantopia
```

---

## Option 2: Run Migration Through GitHub Actions (Automated)

### Add Migration Step to Workflow

If you want migrations to run automatically on deployment, modify `.github/workflows/deploy.yml`:

**Add this section after line 67** (after `pip install -q -r requirements.txt`):

```yaml
        echo "🗄️ Running database migrations..."
        alembic upgrade head
```

This way, every deployment will automatically run pending migrations.

---

## Option 3: Use VS Code Remote SSH (Visual Method)

### Step 1: Install Remote SSH Extension

1. Open VS Code
2. Install "Remote - SSH" extension
3. Press `Ctrl+Shift+P` and select "Remote-SSH: Connect to Host"
4. Enter: `your-username@YOUR_GCP_VM_IP`
5. Enter your password when prompted

### Step 2: Open Terminal in VS Code

1. Once connected, open Terminal (`Ctrl+` ` )
2. Navigate to project: `cd /opt/plantopia/Plantopia`
3. Activate venv: `source venv/bin/activate`
4. Run migration: `alembic upgrade head`

---

## Troubleshooting

### Problem: "alembic: command not found"

**Solution:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall alembic if needed
pip install alembic
```

### Problem: "Database connection failed"

**Solution:**
```bash
# Check database credentials in .env file
cat .env | grep DATABASE

# Test database connection
psql -U your_db_user -d plantopia_db -h localhost

# If connection fails, check if PostgreSQL is running
sudo systemctl status postgresql
```

### Problem: "Target database is not up to date"

**Solution:**
```bash
# Check which migration you're on
alembic current

# See migration history
alembic history --verbose

# Run specific migration if needed
alembic upgrade b9d2f7e8a3c1
```

### Problem: "Migration fails with error"

**Solution:**
```bash
# Check migration logs
alembic upgrade head --sql > migration.sql
cat migration.sql

# Rollback to previous version if needed
alembic downgrade -1

# Check database manually
psql -U your_db_user -d plantopia_db
\dt  # List tables
```

---

## Verification Checklist

After running migration, verify:

- [ ] Migration completed without errors
- [ ] `alembic current` shows `b9d2f7e8a3c1 (head)`
- [ ] Tables exist: `user_plant_chats` and `chat_messages`
- [ ] Application restarted successfully
- [ ] API documentation accessible: `http://YOUR_GCP_IP/docs`
- [ ] New chat endpoints visible in Swagger UI:
  - POST `/chat/general/start`
  - POST `/chat/general/message`
  - POST `/chat/plant/{instance_id}/start`
  - POST `/chat/plant/message`
  - GET `/chat/{chat_id}/history`
  - DELETE `/chat/{chat_id}`

---

## Testing the Chat Feature

### Step 1: Verify Gemini API Keys

```bash
# On GCP server, check if API keys file exists
cd /opt/plantopia/Plantopia
ls -la gemini_api_keys.txt

# If missing, create it
nano gemini_api_keys.txt
```

**Format:**
```
user1,YOUR_GEMINI_API_KEY_1
user2,YOUR_GEMINI_API_KEY_2
user3,YOUR_GEMINI_API_KEY_3
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`)

### Step 2: Restart Application

```bash
sudo supervisorctl restart plantopia
```

### Step 3: Test Chat Endpoint

```bash
# Test general chat start
curl -X POST "http://localhost:8000/api/v1/chat/general/start" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'

# Should return chat_id and success message
```

### Step 4: Access Swagger UI

Open browser: `http://YOUR_GCP_IP/docs`

Test the new chat endpoints interactively!

---

## Post-Deployment Steps

### 1. Set Up Cleanup Cron Job

```bash
# Edit crontab
crontab -e

# Add this line to run cleanup every hour
0 * * * * cd /opt/plantopia/Plantopia && source venv/bin/activate && python -c "from app.services.plant_chat_service import PlantChatService; import asyncio; from app.core.database import get_async_db; async def cleanup(): async with get_async_db() as db: service = PlantChatService(db); deleted = await service.cleanup_expired_chats(); print(f'Deleted {deleted} expired chats'); asyncio.run(cleanup())"
```

Or create a cleanup script:

```bash
# Create cleanup script
nano /opt/plantopia/cleanup_chats.py
```

**cleanup_chats.py:**
```python
import asyncio
from app.services.plant_chat_service import PlantChatService
from app.core.database import get_async_db

async def cleanup():
    async with get_async_db() as db:
        service = PlantChatService(db)
        deleted = await service.cleanup_expired_chats()
        print(f'Deleted {deleted} expired chats at {datetime.now()}')

if __name__ == "__main__":
    asyncio.run(cleanup())
```

**Add to crontab:**
```bash
0 * * * * cd /opt/plantopia/Plantopia && source venv/bin/activate && python cleanup_chats.py >> /var/log/plantopia/chat_cleanup.log 2>&1
```

### 2. Monitor Gemini API Usage

```bash
# Check application logs for API usage
sudo supervisorctl tail -100 plantopia

# Look for lines like:
# "Gemini API call successful with key: user1"
# "Key user1 usage: 15 requests, 5000 tokens today"
```

### 3. Monitor Chat Activity

```bash
# Connect to database
psql -U your_db_user -d plantopia_db

# Check active chats
SELECT count(*) FROM user_plant_chats WHERE is_active = true;

# Check chat messages count
SELECT count(*) FROM chat_messages;

# Check expired chats ready for cleanup
SELECT count(*) FROM user_plant_chats WHERE expires_at < NOW();
```

---

## Quick Reference Commands

```bash
# Connect to GCP
ssh your-username@YOUR_GCP_IP

# Navigate to project
cd /opt/plantopia/Plantopia

# Activate environment
source venv/bin/activate

# Run migration
alembic upgrade head

# Check migration status
alembic current

# Restart app
sudo supervisorctl restart plantopia

# Check app status
sudo supervisorctl status plantopia

# View logs
sudo supervisorctl tail -100 plantopia

# Check database
psql -U your_db_user -d plantopia_db
\dt
\q
```

---

## Rollback (If Needed)

If something goes wrong, you can rollback:

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade a8f3e4b1c5d2

# Restart application
sudo supervisorctl restart plantopia
```

---

## Need Help?

- Check application logs: `sudo supervisorctl tail -100 plantopia`
- Check error logs: `sudo supervisorctl tail -100 plantopia stderr`
- Check supervisor status: `sudo supervisorctl status`
- Restart supervisor: `sudo supervisorctl restart all`

---

## Summary

**Simplest approach:**
```bash
ssh your-username@YOUR_GCP_IP
cd /opt/plantopia/Plantopia
source venv/bin/activate
alembic upgrade head
sudo supervisorctl restart plantopia
```

That's it! Your chat feature should now be live on GCP. 🚀
