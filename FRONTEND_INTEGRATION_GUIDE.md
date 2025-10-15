# Frontend Integration Quick Start Guide
## Phase 1 Backend Endpoints

> **TL;DR**: Replace your localStorage workarounds with these 3 new backend endpoints!

---

## 🎯 Quick Overview

| Your Need | Use This Endpoint | Method |
|-----------|------------------|--------|
| Load checklist progress when opening journal | `/api/v1/tracking/instance/{id}/checklist` | GET |
| Mark setup instructions complete | `/api/v1/tracking/instance/{id}/complete-setup` | POST |
| Determine which step to show | `/api/v1/tracking/instance/{id}/status` | GET |

---

## 🚀 Integration in 3 Steps

### Step 1: Update `loadDetailAndTips()` Function

**Before (localStorage workaround):**
```typescript
const loadDetailAndTips = async () => {
  // ... existing code ...

  // Load from localStorage
  const savedChecklist = localStorage.getItem(`checklist:completed:${instanceId}`);
  if (savedChecklist) {
    checklistCompletedSet.value = new Set(JSON.parse(savedChecklist));
  }
};
```

**After (with backend):**
```typescript
const loadDetailAndTips = async () => {
  // ... existing code ...

  // Load checklist from backend
  try {
    const response = await fetch(
      `/api/v1/tracking/instance/${instanceId}/checklist`
    );
    const data = await response.json();

    // Hydrate completed set
    checklistCompletedSet.value = new Set(
      data.checklist_items
        .filter(item => item.is_completed)
        .map(item => item.item_key)
    );

    // Update progress bar
    checklistProgress.value = data.progress_summary.completion_percentage;

  } catch (error) {
    console.error('Failed to load checklist:', error);
    // Fallback to localStorage if needed
  }
};
```

---

### Step 2: Update Setup Complete Handler

**Before (inferred from is_active):**
```typescript
const handleSetupComplete = async () => {
  // Inferred from growing status
  setupComplete.value = instanceDetails.value?.tracking_info?.is_active || false;
};
```

**After (explicit endpoint):**
```typescript
const handleSetupComplete = async () => {
  try {
    await fetch(
      `/api/v1/tracking/instance/${instanceId}/complete-setup`,
      { method: 'POST' }
    );

    setupComplete.value = true;
    showNotification('Setup completed successfully!');

    // Optionally move to Step 3
    currentStep.value = 3;

  } catch (error) {
    console.error('Failed to complete setup:', error);
    showError('Could not mark setup complete. Please try again.');
  }
};
```

---

### Step 3: Update Modal Open Logic

**Before (multiple API calls + localStorage):**
```typescript
const openJournalModal = async (instanceId) => {
  await loadPlantInstanceDetails();
  await loadPlantRequirements();
  await loadPlantInstructions();

  // Calculate from localStorage
  const progress = calculateChecklistPercentage();
  currentStep.value = progress >= 80 ? 2 : 1;
};
```

**After (single status endpoint):**
```typescript
const openJournalModal = async (instanceId) => {
  try {
    // Single call to get status
    const status = await fetch(
      `/api/v1/tracking/instance/${instanceId}/status`
    ).then(r => r.json());

    // Determine which step to show
    if (status.growing_status.is_active) {
      currentStep.value = 3; // Timeline
    } else if (status.setup_status.completed) {
      currentStep.value = 2; // Setup complete, show timeline prep
    } else if (status.checklist_status.meets_threshold) {
      currentStep.value = 2; // Ready for setup
    } else {
      currentStep.value = 1; // Still working on checklist
    }

    // Enable/disable buttons based on status
    canStartSetup.value = status.checklist_status.meets_threshold;

    // Load step-specific data
    await loadStepData(currentStep.value);

  } catch (error) {
    console.error('Failed to load status:', error);
    // Fallback to Step 1
    currentStep.value = 1;
  }
};
```

---

## 📝 Complete Example: Refactored Journal Component

```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';

const instanceId = ref<number>(123);
const currentStep = ref<number>(1);
const checklistData = ref<any>(null);
const setupCompleted = ref<boolean>(false);

// On modal open
onMounted(async () => {
  await initializeJournal();
});

async function initializeJournal() {
  try {
    // 1. Get status to determine initial step
    const status = await fetch(
      `/api/v1/tracking/instance/${instanceId.value}/status`
    ).then(r => r.json());

    // 2. Determine which step to show
    if (status.growing_status.is_active) {
      currentStep.value = 3;
    } else if (status.setup_status.completed ||
               status.checklist_status.meets_threshold) {
      currentStep.value = 2;
    } else {
      currentStep.value = 1;
    }

    // 3. Store setup completion status
    setupCompleted.value = status.setup_status.completed;

    // 4. Load step-specific data
    if (currentStep.value === 1) {
      await loadChecklist();
    } else if (currentStep.value === 2) {
      await loadSetupInstructions();
    } else {
      await loadTimeline();
    }

  } catch (error) {
    console.error('Failed to initialize journal:', error);
    currentStep.value = 1;
  }
}

async function loadChecklist() {
  const data = await fetch(
    `/api/v1/tracking/instance/${instanceId.value}/checklist`
  ).then(r => r.json());

  checklistData.value = data;

  // Create completed set for UI
  const completedSet = new Set(
    data.checklist_items
      .filter(item => item.is_completed)
      .map(item => item.item_key)
  );

  return completedSet;
}

async function handleChecklistToggle(itemKey: string, isCompleted: boolean) {
  // Mark item complete (existing endpoint)
  await fetch('/api/v1/tracking/checklist/complete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      instance_id: instanceId.value,
      checklist_item_key: itemKey,
      is_completed: isCompleted
    })
  });

  // Reload checklist to get updated progress
  await loadChecklist();
}

async function handleSetupComplete() {
  await fetch(
    `/api/v1/tracking/instance/${instanceId.value}/complete-setup`,
    { method: 'POST' }
  );

  setupCompleted.value = true;
  currentStep.value = 3; // Move to timeline
}

async function handleStartGrowing() {
  await fetch(
    `/api/v1/tracking/instance/${instanceId.value}/start-growing`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_date: new Date().toISOString().split('T')[0]
      })
    }
  );

  // Reload to show timeline
  await initializeJournal();
}
</script>
```

---

## 🔄 Migration Checklist

- [ ] Remove localStorage code for checklist persistence
- [ ] Replace with `/checklist` endpoint call
- [ ] Update setup completion logic to use `/complete-setup` endpoint
- [ ] Replace multiple API calls on modal open with single `/status` call
- [ ] Update button enable/disable logic to use `meets_threshold` flag
- [ ] Test all three steps flow (checklist → setup → timeline)
- [ ] Add error handling with fallback behavior
- [ ] Update UI to show setup completion timestamp
- [ ] Remove inferring setup from `is_active` flag

---

## ⚠️ Important Notes

### Don't Mix Old and New Approaches

**❌ Bad:**
```typescript
// Don't infer setup completion from is_active
if (instanceDetails.is_active) {
  setupComplete.value = true; // WRONG!
}
```

**✅ Good:**
```typescript
// Use the dedicated status endpoint
const status = await fetch(`/api/v1/tracking/instance/${id}/status`)
  .then(r => r.json());
setupComplete.value = status.setup_status.completed;
```

### Setup Complete ≠ Growing Active

- `setup_completed = true` means user finished Step 2 (setup instructions)
- `is_active = true` means user started Step 3 (growing/timeline)
- These are now **independent** flags!

### Threshold for Step 2

Use `meets_threshold` flag from status endpoint:
```typescript
// Enable "Start Setup" button when ready
canStartSetup.value = status.checklist_status.meets_threshold; // >= 80%
```

---

## 🧪 Testing Your Integration

### Manual Test Flow

1. **Open journal modal** → Should show correct step based on status
2. **Toggle checklist items** → Progress bar should update
3. **Reach 80% progress** → "Start Setup" button should enable
4. **Complete setup instructions** → Should mark setup complete
5. **Close and reopen modal** → Should preserve state (no localStorage!)
6. **Start growing** → Should show timeline (Step 3)

### Console Testing

```javascript
// Test in browser console
const instanceId = 1; // Replace with real ID

// 1. Check status
fetch(`/api/v1/tracking/instance/${instanceId}/status`)
  .then(r => r.json())
  .then(console.log);

// 2. Load checklist
fetch(`/api/v1/tracking/instance/${instanceId}/checklist`)
  .then(r => r.json())
  .then(console.log);

// 3. Complete setup
fetch(`/api/v1/tracking/instance/${instanceId}/complete-setup`, {
  method: 'POST'
}).then(r => r.json()).then(console.log);
```

---

## 🐛 Common Issues

### Issue: Checklist returns empty items

**Cause**: Plant doesn't have growth data generated yet

**Solution**:
```typescript
if (data.checklist_items.length === 0) {
  // Initialize checklist first
  await fetch(`/api/v1/tracking/instance/${id}/initialize-checklist`, {
    method: 'POST'
  });

  // Then reload
  await loadChecklist();
}
```

### Issue: Setup complete doesn't persist

**Cause**: Not calling the correct endpoint

**Solution**: Use `/complete-setup` endpoint, not just setting local state:
```typescript
// ❌ Wrong
setupComplete.value = true;

// ✅ Correct
await fetch(`/api/v1/tracking/instance/${id}/complete-setup`, {
  method: 'POST'
});
setupComplete.value = true; // Update UI after API call
```

### Issue: Progress percentage doesn't match UI

**Cause**: Using localStorage percentage instead of backend

**Solution**: Always use `progress_summary.completion_percentage` from API:
```typescript
const { progress_summary } = await fetch(
  `/api/v1/tracking/instance/${id}/checklist`
).then(r => r.json());

progressPercentage.value = progress_summary.completion_percentage;
```

---

## 📚 Additional Resources

- **Full API Documentation**: See `PHASE1_API_DOCUMENTATION.md`
- **Backend Code**: `app/api/endpoints/plant_tracking.py` (lines 686-794)
- **Service Logic**: `app/services/plant_instance_service.py`
- **Database Models**: `app/models/database.py` (UserPlantInstance)

---

## 🤝 Need Help?

If you encounter issues:

1. Check the full API documentation
2. Review the backend implementation
3. Test endpoints directly with `curl` or Postman
4. Check browser console for error messages
5. Verify instance_id is valid

---

**Quick Start Version**: 1.0
**Last Updated**: October 14, 2025
**Status**: ✅ Ready to integrate
