<template>
  <div class="impact-stats">
    <div class="stat-card">
      <div class="stat-value">1,200+</div>
      <div class="stat-label">Active Gardeners</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">45,000<span class="stat-unit">kg</span></div>
      <div class="stat-label">CO2 Absorbed</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">8,500</div>
      <div class="stat-label">Plants Recommended</div>
    </div>
    <div class="stat-card">
      <div class="stat-value">2.8<span class="stat-unit">C</span></div>
      <div class="stat-label">Average Cooling</div>
    </div>
  </div>
</template>

<style scoped>
.impact-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 3rem 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-card {
  text-align: center;
}

.stat-value {
  font-size: 3rem;
  font-weight: 700;
  color: #34d399;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
  margin-bottom: 0.5rem;
}

.stat-unit {
  font-size: 2rem;
  font-weight: 500;
}

.stat-label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}

@media (max-width: 768px) {
  .impact-stats {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }

  .stat-value {
    font-size: 2.5rem;
  }

  .stat-unit {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .impact-stats {
    grid-template-columns: 1fr;
  }

  .stat-value {
    font-size: 2rem;
  }

  .stat-unit {
    font-size: 1.2rem;
  }
}
</style>