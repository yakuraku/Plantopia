<template>
  <div class="features-section">
    <!-- Explore Plants Section -->
    <div class="explore-section">
      <h2 class="section-title">Explore Plants</h2>
      <p class="section-subtitle">Discover your most interest plants</p>

      <div class="explore-grid">
        <!-- Flowers Card -->
        <div class="category-card flowers-card" @click="$emit('navigate-to-plants', 'flowers')">
          <div class="category-content">
            <h3 class="category-title">Flowers</h3>
            <button class="category-btn">Explore Plants</button>
          </div>
          <div class="category-background"></div>
        </div>

        <!-- Vegetables Card -->
        <div class="category-card vegetables-card" @click="$emit('navigate-to-plants', 'vegetables')">
          <div class="category-content">
            <h3 class="category-title">Vegetables</h3>
            <button class="category-btn">Explore Plants</button>
          </div>
          <div class="category-background"></div>
        </div>

        <!-- Herbs Card -->
        <div class="category-card herbs-card" @click="$emit('navigate-to-plants', 'herbs')">
          <div class="category-content">
            <h3 class="category-title">Herbs</h3>
            <button class="category-btn">Explore Plants</button>
          </div>
          <div class="category-background"></div>
        </div>
      </div>
    </div>

    <!-- Smart Recommendations Section -->
    <div class="recommendations-section">
      <div class="recommendations-content">
        <div class="recommendations-icon">
          <SparklesIcon class="icon" />
        </div>
        <div class="recommendations-text">
          <h3 class="recommendations-title">Smart Recommendations</h3>
          <p class="recommendations-description">Get personalized plant suggestions based on your location, space, and climate goals</p>
        </div>
      </div>
      <button class="recommendations-btn" @click="$emit('navigate-to-recommendations')">
        Explore Plants
        <ArrowRightIcon class="btn-arrow" />
      </button>
    </div>

    <!-- Track Your Impact Section -->
    <div class="impact-section">
      <div class="impact-content">
        <div class="impact-icon">
          <ChartBarIcon class="icon" />
        </div>
        <div class="impact-text">
          <h3 class="impact-title">Track Your Impact</h3>
          <p class="impact-description">Visualize your CO2 absorption, cooling effects, and contribution to air quality</p>
        </div>
      </div>
      <button class="impact-btn" @click="$emit('navigate-to-dashboard')">
        View Dashboard
        <ArrowRightIcon class="btn-arrow" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { SparklesIcon, ChartBarIcon, ArrowRightIcon } from '@heroicons/vue/24/outline'

defineEmits<{
  'navigate-to-recommendations': []
  'navigate-to-dashboard': []
  'navigate-to-journey': []
  'navigate-to-plants': [category: 'flowers' | 'vegetables' | 'herbs']
}>()
</script>

<style scoped>
.features-section {
  margin-bottom: 0;
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

/* Explore Plants Section */
.explore-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(15px);
  border-radius: 24px;
  padding: 3rem 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
  text-align: center;
}

.section-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2.5rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
  text-align: center;
}

.explore-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.category-card {
  position: relative;
  height: 200px;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.3);
}

.category-content {
  position: relative;
  z-index: 2;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: flex-start;
  padding: 2rem;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.6));
}

.category-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
}

.category-btn {
  background: transparent;
  color: white;
  border: 2px solid white;
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.category-btn:hover {
  background: white;
  color: #111827;
  transform: translateY(-2px);
}

.category-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1;
  background-size: cover;
  background-position: center;
  transition: transform 0.3s ease;
}

.flowers-card .category-background {
  background-image: url('/Flower.jpg');
}

.vegetables-card .category-background {
  background-image: url('/Vegetable.jpg');
}

.herbs-card .category-background {
  background-image: url('/Herb.jpg');
}

.category-card:hover .category-background {
  transform: scale(1.1);
}

/* Smart Recommendations Section */
.recommendations-section {
  background: rgba(52, 211, 153, 0.1);
  backdrop-filter: blur(15px);
  border-radius: 24px;
  padding: 2.5rem;
  border: 1px solid rgba(52, 211, 153, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.recommendations-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 1;
}

.recommendations-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #34d399, #10b981);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.recommendations-text {
  flex: 1;
}

.recommendations-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}

.recommendations-description {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}

.recommendations-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid white;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.recommendations-btn:hover {
  background: white;
  color: #111827;
  transform: translateY(-2px);
}

/* Track Your Impact Section */
.impact-section {
  background: rgba(59, 130, 246, 0.1);
  backdrop-filter: blur(15px);
  border-radius: 24px;
  padding: 2.5rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
}

.impact-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex: 1;
}

.impact-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #60a5fa, #3b82f6);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.impact-text {
  flex: 1;
}

.impact-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}

.impact-description {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
}

.impact-btn {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 2px solid white;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.impact-btn:hover {
  background: white;
  color: #111827;
  transform: translateY(-2px);
}

.icon {
  width: 40px;
  height: 40px;
  color: white;
  stroke-width: 1.5;
}

.btn-arrow {
  width: 16px;
  height: 16px;
  stroke-width: 2;
}

@media (max-width: 1024px) {
  .recommendations-section,
  .impact-section {
    flex-direction: column;
    text-align: center;
  }

  .recommendations-content,
  .impact-content {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 768px) {
  .explore-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .section-title {
    font-size: 2rem;
  }

  .category-card {
    height: 160px;
  }

  .category-content {
    padding: 1.5rem;
  }

  .category-title {
    font-size: 1.5rem;
  }

  .recommendations-section,
  .impact-section {
    padding: 2rem;
  }

  .recommendations-title,
  .impact-title {
    font-size: 1.5rem;
  }

  .recommendations-icon,
  .impact-icon {
    width: 60px;
    height: 60px;
  }

  .icon {
    width: 30px;
    height: 30px;
  }
}
</style>
