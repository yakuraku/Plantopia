# Iteration 3 - Comprehensive Testing Guide

**Last Updated**: 2025-10-11
**Status**: Ready for Testing

---

## 📁 Quick Navigation

- **TEST_PLAN.md** - Detailed test scenarios and expected behaviors
- **realistic_user_scenarios_test.py** - Main test script
- **reports/** - Test results (JSON + TXT summaries)

---

## 🎯 What This Tests

This comprehensive test suite validates:

1. **Email-Based Authentication**
   - Auto-user creation on first API call
   - Email as primary identifier across all endpoints
   - No Google OAuth dependencies

2. **Plant Tracking Workflow**
   - Starting plant tracking with Gemini API integration
   - Requirements checklist generation
   - Setup instructions
   - Timeline with actual calendar dates
   - Multi-plant management per user

3. **Data Reuse Logic**
   - First user for a plant → Gemini API call (generates data)
   - Subsequent users for same plant → Reuse existing data (no API call)
   - Validates token/API cost optimization

4. **Chat Functionality**
   - General agriculture Q&A chat
   - Plant-specific chat with context
   - Message history
   - Token tracking

5. **Favorites System**
   - Plant favorites (add, remove, check, list)
   - Guide favorites (add, remove, check, list)

6. **Guide Management**
   - Browse guides by category
   - Get guide content
   - Favorite guides

---

## 👥 Test Users

### Sarah Johnson
- Email: `sarah.johnson.test@plantopia.com`
- Type: Beginner, Balcony Gardener
- Plants: 3 (Carrot, Cherry Tomato, Basil)
- Purpose: Test first-time user experience, Gemini API calls

### Mike Chen
- Email: `mike.chen.test@plantopia.com`
- Type: Advanced, Backyard Gardener
- Plants: 4 (Carrot, Capsicum, Lettuce, Zucchini)
- Purpose: Test data reuse, multi-plant management

---

## 🚀 Running Tests

### On Local Machine (for VM deployment)

```bash
# Navigate to test directory
cd tests/iteration_3

# Run test script (will use localhost:8000 by default)
python realistic_user_scenarios_test.py

# Or specify VM URL
python realistic_user_scenarios_test.py http://YOUR_VM_IP:8000/api/v1
```

### On GCP VM (after deployment)

```bash
# SSH into VM
ssh your-user@your-vm-ip

# Navigate to project
cd /opt/plantopia/Plantopia/tests/iteration_3

# Activate environment
source ../../venv/bin/activate

# Run tests against local server
python realistic_user_scenarios_test.py http://localhost:8000/api/v1

# Check results
ls -la reports/
cat reports/realistic_scenarios_*.txt
```

### Download Results from VM

```bash
# From your local machine
scp your-user@your-vm-ip:/opt/plantopia/Plantopia/tests/iteration_3/reports/* ./reports/
```

---

## 📊 Understanding Test Results

### JSON Report (`realistic_scenarios_YYYYMMDD_HHMMSS.json`)

Contains detailed results for each test:
```json
{
  "timestamp": "2025-10-11T12:00:00",
  "total_tests": 25,
  "passed": 24,
  "failed": 1,
  "test_results": [
    {
      "test_name": "Sarah - Start Carrot (Day 0)",
      "status": "PASS",
      "timestamp": "2025-10-11T12:00:01",
      "details": {
        "instance_id": 123,
        "response_time_ms": 2345,
        "expected": "Auto-create user, call Gemini API"
      }
    }
  ]
}
```

### Text Summary (`realistic_scenarios_YYYYMMDD_HHMMSS.txt`)

Human-readable summary:
```
==========================================
REALISTIC USER SCENARIOS TEST SUMMARY
==========================================

Total Tests: 25
Passed: 24
Failed: 1
Success Rate: 96.0%

[PASS] Sarah - Start Carrot (Day 0)
  Response Time: 2345ms

[FAIL] Mike - Send Plant Chat Message
  Error: Connection timeout
```

---

## 🔍 Test Scenarios Covered

### Scenario 1: Sarah - First Plant (Carrot, Day 0)
**Tests**: 5
- Start tracking → Auto-create user + Gemini API call
- Get plant details → Timeline with calendar dates
- Get requirements checklist → Gemini-generated list
- Complete checklist items → Progress tracking
- Get setup instructions → Step-by-step guide

**Expected Gemini API Call**: ✅ YES (first time for this plant)

### Scenario 2: Sarah - Add More Plants
**Tests**: 3
- Add Cherry Tomato (Day 25) → Existing user recognized
- Add Basil (Day 15) → Indoor plant tracking
- Get all plants → List with different stages/progress

### Scenario 3: Mike - Carrot (Data Reuse Test)
**Tests**: 1
- Start same Carrot as Sarah → **REUSE plant_growth_data**
- Expected Response Time: < 1 second (no Gemini call)

**Expected Gemini API Call**: ❌ NO (reuse Sarah's data)

### Scenario 4: Mike - Multi-Plant Management
**Tests**: 2
- Add 3 more plants (Capsicum, Lettuce, Zucchini)
- Get all plants → 4 plants with different stages

### Scenario 5: Sarah - General Agriculture Chat
**Tests**: 3
- Start general chat session
- Send 2 messages → AI responses with token tracking
- Get chat history → All messages retrieved

### Scenario 6: Mike - Plant-Specific Chat
**Tests**: 2
- Start plant-specific chat for Carrot
- Ask plant question → AI with plant context

### Scenario 7: Plant Favorites
**Tests**: 2
- Add plant favorites (Carrot, Basil)
- Get favorites list

### Scenario 8: Guide Browsing & Favorites
**Tests**: 3
- Get guide categories
- Browse Composting guides + favorite one
- Get guide favorites list

---

## ✅ Success Criteria

### Must Pass
- [ ] All users auto-created (2 users)
- [ ] Plant instances created (7 total)
- [ ] Gemini API called for new plants only
- [ ] Mike's Carrot reuses Sarah's data (fast response)
- [ ] Timeline dates calculated correctly
- [ ] Chat sessions created and working
- [ ] Favorites working (plants + guides)

### Performance
- [ ] Non-Gemini API calls: < 500ms
- [ ] Gemini API calls: 2-5 seconds (acceptable)
- [ ] Data reuse calls: < 1 second (no Gemini)

### Data Integrity
- [ ] No duplicate user entries
- [ ] plant_growth_data shared across users
- [ ] user_plant_instances separate per user
- [ ] Favorites unique per user
- [ ] Token counts accurate

---

## 🐛 Troubleshooting

### Test Connection Errors
```
Error: Connection refused
```
**Solution**: Verify server is running:
```bash
curl http://localhost:8000/api/v1/health
```

### Gemini API Errors
```
Error: GEMINI_API_KEY not found
```
**Solution**: Check environment variables on VM:
```bash
echo $GEMINI_API_KEY
```

### Database Errors
```
Error: User with email X not found
```
**Solution**: Run database migration:
```bash
alembic upgrade head
```

### Import Errors
```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: Install dependencies:
```bash
pip install requests
```

---

## 📝 After Testing

### Review Checklist
1. Check test success rate (goal: > 95%)
2. Verify Gemini API calls are minimal (data reuse working)
3. Review response times (performance)
4. Check database for correct data
5. Verify no duplicate users created
6. Confirm favorites are user-specific

### Report Issues
If tests fail, document:
- Test name that failed
- Expected vs actual behavior
- Error messages
- Response times
- Database state (if relevant)

---

## 🔄 Iterative Testing Cycle

1. **Run tests on VM** → Generate reports
2. **Download reports** → Review locally
3. **Identify issues** → Update code
4. **Commit changes** → GitHub Actions deploys
5. **Repeat** → Test again

---

**Happy Testing! 🧪**
