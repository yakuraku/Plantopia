# 🚀 Start Here - Testing Guide

**Status**: ✅ Everything Ready
**Last Updated**: 2025-10-11

---

## ⚡ Quick Start (3 Steps)

### 1. Wait for Deployment
GitHub Actions is deploying your code to GCP VM right now.

**Check deployment status**:
- Go to: https://github.com/yakuraku/Plantopia/actions
- Wait for green checkmark ✅

### 2. SSH into VM and Run Tests
```bash
# SSH into your GCP VM
ssh your-user@your-vm-ip

# Navigate to tests
cd /opt/plantopia/Plantopia/tests/iteration_3

# Activate Python environment
source ../../venv/bin/activate

# Run comprehensive test suite
python realistic_user_scenarios_test.py http://localhost:8000/api/v1

# This will take 2-3 minutes (includes Gemini API calls)
```

### 3. View Results
```bash
# View summary (on VM)
cat reports/realistic_scenarios_*.txt

# Or download to local machine
# From your local machine:
scp your-user@your-vm-ip:/opt/plantopia/Plantopia/tests/iteration_3/reports/* ./reports/
```

---

## 📋 What Will Be Tested

### ✅ 2 Realistic Users
1. **Sarah Johnson** - Beginner, balcony gardener (3 plants)
2. **Mike Chen** - Advanced, backyard gardener (4 plants)

### ✅ 8 Complete Scenarios
1. Sarah starts her first plant (Carrot) → Gemini API call
2. Sarah adds more plants (Cherry Tomato, Basil)
3. Mike starts same Carrot → **Data reuse (no Gemini call)**
4. Mike adds 3 more plants (Capsicum, Lettuce, Zucchini)
5. Sarah uses general agriculture chat
6. Mike uses plant-specific chat for Carrot
7. Both users add plant favorites
8. Both users browse and favorite guides

### ✅ 25 API Endpoints
- Plant tracking (8 endpoints)
- Chat (5 endpoints)
- Plant favorites (4 endpoints)
- Guide management (8 endpoints)

---

## 🎯 Expected Results

### Success Metrics
```
Total Tests: 25
Passed: 25 (100%)
Failed: 0

Users Created: 2 (Sarah, Mike)
Plant Instances: 7
Gemini API Calls: ~6 (Carrot reused for Mike)
Chat Sessions: 2
Response Times: < 500ms (non-Gemini)
```

### Key Validation
**Data Reuse Test** (Most Important!):
```
✅ Sarah's Carrot: Response time 2-5s (Gemini API called)
✅ Mike's Carrot: Response time < 1s (Data reused, no Gemini call)
```

---

## 📁 Documentation

Read these in order:

1. **TESTING_READY.md** - Quick overview & API reference
2. **TEST_PLAN.md** - Detailed scenarios & expected behaviors
3. **README_TESTING.md** - Troubleshooting & detailed guide

---

## 🐛 Troubleshooting

### Tests Won't Start
**Check server is running**:
```bash
curl http://localhost:8000/api/v1/health
```

If not running:
```bash
sudo supervisorctl status plantopia
sudo supervisorctl start plantopia
```

### Gemini API Errors
**Check API key**:
```bash
echo $GEMINI_API_KEY
```

If empty, set it:
```bash
export GEMINI_API_KEY="your-api-key"
```

### Module Not Found
**Install dependencies**:
```bash
pip install requests
```

---

## 📊 After Testing

### Review Checklist
- [ ] Check success rate (goal: 100%)
- [ ] Verify Mike's Carrot was fast (< 1s = data reused)
- [ ] Count Gemini API calls (should be ~6, not 7)
- [ ] Check response times (most < 500ms)
- [ ] Review any failures in detail

### Share Results
**From VM, copy reports to local**:
```bash
# On local machine
cd D:\MAIN_PROJECT\Plantopia\tests\iteration_3
scp your-user@your-vm-ip:/opt/plantopia/Plantopia/tests/iteration_3/reports/* ./reports/
```

Then I can analyze the results!

---

## 🔄 If Issues Found

1. **Document the issue**
   - Which test failed?
   - Expected vs actual behavior
   - Error messages

2. **I'll fix the code**
   - Update endpoints/services as needed
   - Commit changes

3. **GitHub Actions deploys automatically**
   - Wait for deployment
   - Run tests again

4. **Iterate until 100%**

---

## 💡 Pro Tips

- **Run tests multiple times** to ensure consistency
- **Check database** after tests to verify data
- **Monitor Gemini quota** - Track API usage
- **Save reports** - Compare before/after fixes

---

## ✨ What Makes This Test Special

1. **Realistic Users** - Not just API calls, but actual user journeys
2. **Data Reuse Validation** - Proves Gemini API optimization works
3. **Multi-Plant Scenarios** - Tests complex real-world usage
4. **Complete Feature Coverage** - All 25 endpoints tested
5. **Detailed Reporting** - JSON + human-readable summaries

---

## 🎉 Ready to Go!

Everything is set up. Just:
1. Wait for deployment ✅
2. SSH into VM and run the test script
3. Review results
4. Let me know what you find!

**Test Command**:
```bash
python realistic_user_scenarios_test.py http://localhost:8000/api/v1
```

Good luck! 🍀
