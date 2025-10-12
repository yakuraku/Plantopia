# Next Steps - Quick Reference

**Schema Fix Status:** Pushed to main (commit `a08cda9`)
**Deployment:** Check GitHub Actions at https://github.com/yakuraku/Plantopia/actions

---

## ⚡ IMMEDIATE ACTIONS

### 1. Monitor Deployment
```bash
# Check GitHub Actions status in your browser:
# https://github.com/yakuraku/Plantopia/actions
#
# Wait for "Deploy to GCP" workflow to complete (usually ~5-10 minutes)
# Look for green checkmark ✓
```

### 2. Re-run Tests on VM
```bash
# SSH to your VM
ssh ykur@YOUR_VM_IP

# Run the test suite
sudo bash /opt/plantopia/Plantopia/tests/iteration_3/run_tests_on_vm.sh
```

**Expected Results After Schema Fix:**
- ✅ Plant Tracking: 2/2 tests should PASS (was 0/2)
- ✅ Workflows: 5/5 steps should PASS (was 3/5)
- ⚠️ Plant Chat: Still 3/4 (1 test needs user fix)
- **Total: 10/11 tests (90.91%)** - Up from 6/11 (54.55%)

### 3. Download New Reports
```bash
# Use FileZilla to download from VM:
# Remote path: /opt/plantopia/Plantopia/tests/iteration_3/reports/
# Local path: D:\MAIN_PROJECT\Plantopia\tests\iteration_3\reports\
#
# Download all new JSON files with today's timestamp
```

---

## 🔧 FIX REMAINING ISSUE (Optional - For 100%)

### Issue: Missing Test User
The last failing test needs user_id=1 to exist in database.

**Quick Fix - Create Test User:**
```bash
# SSH to VM
ssh ykur@YOUR_VM_IP

# Connect to PostgreSQL
sudo -u postgres psql plantopia_db

# Create test user
INSERT INTO users (id, email, name, suburb_id, created_at)
VALUES (
    1,
    'test@plantopia.com',
    'Test User',
    1,
    NOW()
);

# Verify
SELECT id, email, name FROM users WHERE id = 1;

# Exit
\q
```

**Alternative - Use Existing User:**
```bash
# Find existing users
sudo -u postgres psql plantopia_db -c "SELECT id, email, name FROM users LIMIT 5;"

# Update test files to use that user_id instead of 1
# Files to update:
# - tests/iteration_3/test_plant_chat_live.py
# - tests/iteration_3/test_end_to_end_workflow.py
# - tests/iteration_3/fixtures/test_data.json
```

### 4. Final Test Run (After User Fix)
```bash
# Run tests one more time
sudo bash /opt/plantopia/Plantopia/tests/iteration_3/run_tests_on_vm.sh

# Expected: 11/11 tests pass (100%) ✅
```

---

## 📊 VERIFICATION CHECKLIST

After re-running tests, verify these specific fixes:

### Schema Fix Verification:
- [ ] `POST /tracking/start` returns 201 (not 500)
- [ ] Test: "Start Plant Tracking - Success" = PASS
- [ ] Test: "Start Plant Tracking - Invalid Plant ID" = PASS (with 404)
- [ ] Workflow: "New User Complete Journey - Start Tracking" = PASS
- [ ] Workflow: "Progress Tracking Through Stages - Start Tracking" = PASS

### User Fix Verification (after creating user):
- [ ] `POST /chat/general/start` returns 201 (not 500)
- [ ] Test: "Start General Chat - Success" = PASS
- [ ] No foreign key errors in chat tests

---

## 📝 UPDATE PRIMARY REPORT

Once all tests pass, update the team report:

```bash
# Edit IT3_PRIMARY_TEST_REPORT.md
#
# Update sections:
# - Overall Pass Rate: 54.55% → 100%
# - Move failed tests to "PASSED TESTS" section
# - Add "All Issues Resolved" section
# - Update "Validation Status" to "Complete"
```

---

## 🎉 SUCCESS INDICATORS

You'll know everything works when you see:

```
ITERATION 3 - COMPREHENSIVE TEST SUMMARY
======================================================================
OVERALL SUMMARY
======================================================================
Total Tests: 11
Passed: 11
Failed: 0
Pass Rate: 100.00%
```

---

## 💡 TROUBLESHOOTING

### If deployment fails:
- Check GitHub Actions logs for errors
- Verify permissions on VM are correct
- Ensure supervisor restarted the backend service

### If tests still fail after schema fix:
- Check backend logs: `sudo journalctl -u supervisor -n 100`
- Verify schema change is deployed: `cat /opt/plantopia/Plantopia/app/schemas/plant_tracking.py | grep -A 5 "class StartTrackingRequest"`
- Restart backend: `sudo supervisorctl restart plantopia-backend`

### If user creation fails:
- Check if user table exists: `sudo -u postgres psql plantopia_db -c "\dt users"`
- Check table structure: `sudo -u postgres psql plantopia_db -c "\d users"`
- Verify migrations ran: `ls -la alembic/versions/`

---

**GitHub Actions:** https://github.com/yakuraku/Plantopia/actions
**Test Reports Location (VM):** `/opt/plantopia/Plantopia/tests/iteration_3/reports/`
**Test Reports Location (Local):** `D:\MAIN_PROJECT\Plantopia\tests\iteration_3\reports\`
