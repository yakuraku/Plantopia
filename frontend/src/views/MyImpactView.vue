<template>
  <div class="my-impact">
    <div class="page-container">
      <h1 class="page-title">My Climate Impact Journey</h1>
      <div class="content-card">
        <p class="placeholder-text">Impact tracking content will be implemented here...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped>
.my-impact {
  min-height: calc(100vh - 64px);
  background: #f9fafb;
  padding: 2rem 0;
}

.page-container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 2rem;
}

.page-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 2rem;
}

.content-card {
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow:
    0 1px 3px 0 rgba(0, 0, 0, 0.1),
    0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.placeholder-text {
  color: #6b7280;
  font-size: 1rem;
}
</style>
