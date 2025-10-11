# Iteration 3 Testing - Simple Workflow

Complete backend testing for Iteration 3 (Plant Tracking & Chat Features)

## Simple 3-Step Process

### Step 1: Commit & Deploy to GCP
```bash
# Commit your changes to main branch
git add .
git commit -m "feat: iteration 3 testing ready"
git push origin main
```

GitHub Actions will automatically:
- Deploy to your GCP VM
- Run database migrations
- Restart the backend service

**Monitor deployment:** https://github.com/your-repo/actions

### Step 2: Run Tests on GCP VM

After deployment succeeds, SSH into your VM and run:

```bash
# SSH to VM
ssh your-user@your-vm-ip

# Run tests
bash /opt/plantopia/Plantopia/tests/iteration_3/run_tests_on_vm.sh
```

Tests will:
- Run all 19 endpoints (plant tracking + chat)
- Test 59+ scenarios
- Generate detailed reports
- Save results to `tests/iteration_3/reports/`

**Duration:** ~2-3 minutes

### Step 3: Download Reports to Your PC

From your **local PC**, run:

```bash
python tests/iteration_3/download_reports.py
```

This will:
- Connect to your VM via SCP
- Download all test reports
- Save to `tests/iteration_3/reports/` on your PC
- Display latest summary automatically

## What Gets Tested

### Plant Tracking (13 endpoints)
- ✅ Start tracking plants
- ✅ Get user's plants
- ✅ Update progress
- ✅ AI-generated requirements, instructions, timeline
- ✅ Stage-specific tips
- ✅ Checklist management
- ✅ Nickname updates
- ✅ Deactivate instances

### Plant Chat (6 endpoints)
- ✅ General agriculture chat
- ✅ Plant-specific chat with context
- ✅ Image uploads (base64)
- ✅ Chat history
- ✅ Token limit handling
- ✅ Ownership validation

### Workflows (3 complete journeys)
- ✅ New user complete journey (10 steps)
- ✅ Progress tracking through stages (8 steps)
- ✅ Multi-plant management

## Test Reports

After downloading, you'll find:

```
tests/iteration_3/reports/
├── comprehensive_results_YYYYMMDD_HHMMSS.json  # All test details
├── plant_tracking_results_YYYYMMDD_HHMMSS.json # Plant tracking tests
├── plant_chat_results_YYYYMMDD_HHMMSS.json     # Chat tests
├── workflow_results_YYYYMMDD_HHMMSS.json       # Workflow tests
└── summary_YYYYMMDD_HHMMSS.txt                  # Human-readable summary
```

**Open in your favorite editor/IDE to view results**

## Clean Up Test Data

After reviewing results, clean up test data:

```bash
# On your VM (via SSH)
cd /opt/plantopia/Plantopia
source venv/bin/activate

# Preview what will be deleted
python tests/iteration_3/cleanup_test_data.py --dry-run

# Actually delete
python tests/iteration_3/cleanup_test_data.py
```

This removes:
- Test user (`iteration3.test@plantopia.com`)
- All plant instances created by test user
- All chat sessions and messages
- Related progress tracking records

## Troubleshooting

### Deployment Failed
1. Check GitHub Actions logs
2. Verify database migrations ran successfully
3. Check if backend service is running:
   ```bash
   ssh your-user@your-vm-ip
   sudo supervisorctl status plantopia
   ```

### Tests Failed
1. Check test reports for specific errors
2. Verify Gemini API keys are configured on VM
3. Check backend logs:
   ```bash
   sudo supervisorctl tail plantopia
   ```

### Cannot Download Reports
1. Verify SSH access to VM works
2. Check reports exist on VM:
   ```bash
   ls -la /opt/plantopia/Plantopia/tests/iteration_3/reports/
   ```
3. On Windows: Use Git Bash or WinSCP

## Expected Results

**Success Criteria:**
- ✅ Pass rate: 95-100%
- ✅ Duration: 2-3 minutes
- ✅ All endpoints return correct status codes
- ✅ Data persists correctly
- ✅ AI generates valid responses

## Quick Reference

```bash
# 1. Deploy
git push origin main

# 2. Run tests (on VM)
ssh user@vm-ip
bash /opt/plantopia/Plantopia/tests/iteration_3/run_tests_on_vm.sh

# 3. Download reports (on local PC)
python tests/iteration_3/download_reports.py

# 4. Clean up (on VM)
python tests/iteration_3/cleanup_test_data.py
```

---

**Simple. Automated. Documented.**
