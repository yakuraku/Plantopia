<template>
  <div class="cta-section">
    <h2 class="cta-title">Ready to Start Your Climate Garden?</h2>
    <p class="cta-description">
      Join thousands of Melburnians creating beautiful, climate-smart gardens that make a real
      difference
    </p>
    <button class="cta-btn" @click="$emit('navigate-to-recommendations')">
      Get My Plant Recommendations
      <ArrowRightIcon class="cta-arrow" />
    </button>
  </div>
</template>

<script setup lang="ts">
import { ArrowRightIcon } from '@heroicons/vue/24/outline'

defineEmits<{
  'navigate-to-recommendations': []
}>()
</script>

<style scoped>
.cta-section {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(15px);
  border-radius: 20px;
  padding: 3rem 2rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.7);
}

.cta-description {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 2rem;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.7);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.cta-btn {
  background: linear-gradient(135deg, #34d399, #10b981);
  color: white;
  border: none;
  padding: 1.2rem 2.5rem;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 8px 20px rgba(52, 211, 153, 0.3);
}

.cta-btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(52, 211, 153, 0.4);
  background: linear-gradient(135deg, #10b981, #059669);
}

.cta-arrow {
  width: 20px;
  height: 20px;
  stroke-width: 2;
}

@media (max-width: 768px) {
  .cta-title {
    font-size: 2rem;
  }
}
</style>