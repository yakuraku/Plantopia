# Quick Start - Iteration 3 Testing

## Ultra-Simple 3-Step Workflow

### 1️⃣ Deploy to GCP
```bash
git add .
git commit -m "test: iteration 3 testing"
git push origin main
```
Wait for GitHub Actions to complete ✅

### 2️⃣ Run Tests on VM
```bash
ssh your-user@your-vm-ip
bash /opt/plantopia/Plantopia/tests/iteration_3/run_tests_on_vm.sh
```
Wait 2-3 minutes ⏱️

### 3️⃣ Download Results to PC
```bash
# On your local PC
python tests/iteration_3/download_reports.py
```
View reports in `tests/iteration_3/reports/` 📊

## That's It!

**Clean up when done:**
```bash
# SSH to VM
python tests/iteration_3/cleanup_test_data.py
```

---

**Full documentation:** See `README.md`
