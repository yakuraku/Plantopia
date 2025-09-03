<template>
  <div class="features-section">
    <h2 class="features-title">Transform Your Space, Transform the Climate</h2>
    <p class="features-subtitle">
      Join Melbourne's growing community of climate gardeners making a real environmental
      impact
    </p>

    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">
          <SparklesIcon class="icon" />
        </div>
        <h3 class="feature-title">Smart Recommendations</h3>
        <p class="feature-description">
          Get personalized plant suggestions based on your location, space, and climate goals
        </p>
        <button class="feature-btn" @click="$emit('navigate-to-recommendations')">
          Explore Plants
          <ArrowRightIcon class="btn-arrow" />
        </button>
      </div>

      <div class="feature-card">
        <div class="feature-icon feature-icon-blue">
          <ChartBarIcon class="icon" />
        </div>
        <h3 class="feature-title">Track Your Impact</h3>
        <p class="feature-description">
          Visualize your CO2 absorption, cooling effects, and contribution to air quality
        </p>
        <button class="feature-btn" @click="$emit('navigate-to-dashboard')">
          View Dashboard
          <ArrowRightIcon class="btn-arrow" />
        </button>
      </div>

      <div class="feature-card">
        <div class="feature-icon">
          <BookOpenIcon class="icon" />
        </div>
        <h3 class="feature-title">Earn & Achieve</h3>
        <p class="feature-description">
          Complete challenges, earn badges, and compete with your community
        </p>
        <button class="feature-btn" @click="$emit('navigate-to-journey')">
          Start Journey
          <ArrowRightIcon class="btn-arrow" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { SparklesIcon, ChartBarIcon, BookOpenIcon, ArrowRightIcon } from '@heroicons/vue/24/outline'

defineEmits<{
  'navigate-to-recommendations': []
  'navigate-to-dashboard': []
  'navigate-to-journey': []
}>()
</script>

<style scoped>
.features-section {
  margin-bottom: 4rem;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 3rem 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.features-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}

.features-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2.5rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.feature-card {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 2rem;
  text-align: center;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-5px);
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(52, 211, 153, 0.3);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.feature-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #34d399, #10b981);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1.5rem;
}

.feature-icon-blue {
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
}

.icon {
  width: 40px;
  height: 40px;
  color: white;
  stroke-width: 1.5;
}

.feature-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}

.feature-description {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  margin-bottom: 1.5rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}

.feature-btn {
  background: transparent;
  color: white;
  border: 1px solid white;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.feature-btn:hover {
  background: white;
  color: #111827;
  transform: translateY(-2px);
}

.btn-arrow {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .features-title {
    font-size: 2rem;
  }

  .feature-card {
    padding: 1.5rem;
  }

  .feature-icon {
    width: 60px;
    height: 60px;
  }

  .icon {
    width: 30px;
    height: 30px;
  }
}
</style>