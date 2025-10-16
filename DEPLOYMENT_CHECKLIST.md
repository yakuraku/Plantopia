# Phase 1 Deployment Checklist - GCP Backend VM

## 📋 Pre-Deployment Verification

✅ **Commit Status**: Successfully pushed to `main` branch (commit: `ec9cd43`)

✅ **Files Changed**:
- ✅ `app/api/endpoints/plant_tracking.py` - Added 3 new endpoints
- ✅ `app/models/database.py` - Added setup_completed fields
- ✅ `app/schemas/plant_tracking.py` - Added response schemas
- ✅ `app/services/plant_instance_service.py` - Added service methods
- ✅ `app/services/progress_tracking_service.py` - Added checklist retrieval
- ✅ `alembic/versions/f9e4d3b2a1c0_add_setup_completed_fields.py` - Database migration

✅ **Documentation Created**:
- ✅ `PHASE1_API_DOCUMENTATION.md`
- ✅ `FRONTEND_INTEGRATION_GUIDE.md`

---

## 🚀 GCP VM Deployment Steps

### Step 1: SSH into GCP VM

```bash
# SSH into your GCP VM (adjust with your actual details)
gcloud compute ssh plantopia-backend-vm --zone=<your-zone>

# Or use SSH directly
ssh -i ~/.ssh/your-key user@<your-vm-ip>
```

---

### Step 2: Pull Latest Changes

```bash
# Navigate to project directory
cd /path/to/Plantopia

# Pull latest changes from main branch
git pull origin main

# Verify correct commit
git log -1 --oneline
# Should show: ec9cd43 feat: implement Phase 1 enhanced journal tracking endpoints
```

---

### Step 3: Run Database Migration

```bash
# Activate virtual environment (if using one)
source venv/bin/activate  # or your venv path

# Run Alembic migration
python -m alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade c2d8e9f1a4b3 -> f9e4d3b2a1c0, Add setup_completed fields to user_plant_instances
```

**Verify Migration:**
```bash
# Check current migration version
python -m alembic current

# Should show: f9e4d3b2a1c0 (head)
```

---

### Step 4: Verify Database Schema

```bash
# Connect to PostgreSQL
psql -U your_db_user -d plantopia_db

# Verify new columns exist
\d user_plant_instances

# Should see:
# setup_completed          | boolean                  | not null default false
# setup_completed_at       | timestamp with time zone |
```

```sql
-- Check existing data
SELECT id, plant_nickname, setup_completed, setup_completed_at
FROM user_plant_instances
LIMIT 5;

-- Exit psql
\q
```

---

### Step 5: Restart Backend Service

```bash
# If using systemd service
sudo systemctl restart plantopia-backend

# Or if using PM2
pm2 restart plantopia-backend

# Or if using Docker
docker-compose restart backend

# Or if running manually with uvicorn
# Kill existing process and restart
pkill -f "uvicorn app.main:app"
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

---

### Step 6: Verify Backend is Running

```bash
# Check service status
sudo systemctl status plantopia-backend

# Or check process
ps aux | grep uvicorn

# Check logs
sudo journalctl -u plantopia-backend -f

# Or if using PM2
pm2 logs plantopia-backend
```

---

### Step 7: Test New Endpoints

```bash
# Set your backend URL
BACKEND_URL="http://localhost:8000"  # or your actual URL

# 1. Test status endpoint (replace 1 with valid instance_id)
curl "$BACKEND_URL/api/v1/tracking/instance/1/status"

# Expected: JSON response with checklist_status, setup_status, growing_status

# 2. Test checklist endpoint
curl "$BACKEND_URL/api/v1/tracking/instance/1/checklist"

# Expected: JSON response with checklist_items and progress_summary

# 3. Test complete-setup endpoint
curl -X POST "$BACKEND_URL/api/v1/tracking/instance/1/complete-setup"

# Expected: JSON response with setup_completed: true and timestamp
```

---

## ✅ Post-Deployment Verification

### Check 1: Endpoints Accessible

- [ ] `GET /api/v1/tracking/instance/{id}/status` returns 200 OK
- [ ] `GET /api/v1/tracking/instance/{id}/checklist` returns 200 OK
- [ ] `POST /api/v1/tracking/instance/{id}/complete-setup` returns 200 OK

### Check 2: Database Schema

- [ ] `setup_completed` column exists in `user_plant_instances`
- [ ] `setup_completed_at` column exists in `user_plant_instances`
- [ ] Default values are correct (false for setup_completed)

### Check 3: Response Format

- [ ] Status endpoint returns checklist, setup, and growing status
- [ ] Checklist endpoint returns items with all required fields
- [ ] Complete-setup endpoint sets timestamp correctly

### Check 4: Error Handling

- [ ] Invalid instance_id returns 404
- [ ] Non-existent endpoints return 404
- [ ] Server errors return 500 with error message

### Check 5: CORS Configuration

- [ ] Frontend can call endpoints from allowed origins
- [ ] OPTIONS requests return correct CORS headers

---

## 🔍 Troubleshooting

### Issue: Migration Fails

**Error**: `sqlalchemy.exc.ProgrammingError: column "setup_completed" already exists`

**Solution**: Migration already applied. Check current version:
```bash
python -m alembic current
```

If needed, downgrade and reapply:
```bash
python -m alembic downgrade -1
python -m alembic upgrade head
```

---

### Issue: Backend Won't Start

**Check logs for errors**:
```bash
sudo journalctl -u plantopia-backend -n 50
```

**Common causes**:
- Database connection issues (check connection string)
- Import errors (verify all dependencies installed)
- Port already in use (check with `netstat -tulpn | grep 8000`)

**Solution**: Fix error and restart service

---

### Issue: Endpoints Return 404

**Verify routes are registered**:
```bash
# Check if endpoints are listed
curl http://localhost:8000/docs

# Or check OpenAPI spec
curl http://localhost:8000/openapi.json | grep "/tracking/instance"
```

**Solution**: Ensure `app/api/endpoints/plant_tracking.py` is imported correctly

---

### Issue: Database Connection Error

**Check database is running**:
```bash
sudo systemctl status postgresql

# Or
docker ps | grep postgres
```

**Test connection**:
```bash
psql -U your_db_user -d plantopia_db -c "SELECT 1;"
```

**Solution**: Start database service or fix connection string

---

## 📊 Performance Monitoring

After deployment, monitor:

1. **Response Times**:
   - Status endpoint: < 100ms
   - Checklist endpoint: < 150ms
   - Complete-setup endpoint: < 50ms

2. **Error Rates**:
   - 4xx errors: Should be < 1% (mostly user errors)
   - 5xx errors: Should be 0%

3. **Database Queries**:
   - No N+1 query issues
   - Proper use of indexes

---

## 🔄 Rollback Plan (If Needed)

If critical issues occur:

### Step 1: Revert Code
```bash
cd /path/to/Plantopia
git revert ec9cd43
git push origin main
```

### Step 2: Rollback Database
```bash
python -m alembic downgrade -1
```

### Step 3: Restart Service
```bash
sudo systemctl restart plantopia-backend
```

---

## 📝 Deployment Log Template

```
Deployment Date: YYYY-MM-DD HH:MM
Deployed By: [Your Name]
Commit Hash: ec9cd43
Environment: [Production/Staging]

Pre-Deployment Checks:
- [✓] Code pulled successfully
- [✓] Migration ran successfully
- [✓] Service restarted
- [✓] Endpoints tested

Post-Deployment Checks:
- [✓] All endpoints responding
- [✓] No errors in logs
- [✓] Database schema correct
- [✓] CORS working

Issues Encountered: [None / List issues]

Notes: [Any additional notes]
```

---

## 🎯 Success Criteria

Deployment is successful when:

✅ All three Phase 1 endpoints return correct responses
✅ Database migration applied without errors
✅ Backend service running without errors
✅ No increase in error rates
✅ Frontend can successfully call new endpoints
✅ Users can see checklist progress persist across sessions

---

## 📞 Support

If you encounter issues during deployment:

1. Check backend logs: `sudo journalctl -u plantopia-backend -f`
2. Check database logs: `sudo journalctl -u postgresql -f`
3. Review `PHASE1_API_DOCUMENTATION.md` for endpoint details
4. Check commit diff: `git show ec9cd43`

---

**Deployment Version**: Phase 1
**Last Updated**: October 14, 2025
**Status**: Ready for Deployment
