<template>
  <div class="stat-bar">
    <div class="stat-header">
      <span class="stat-icon">{{ icon }}</span>
      <span class="stat-label">{{ label }}</span>
      <span class="stat-value">{{ Math.round(value) }}%</span>
    </div>
    <div class="progress-container">
      <div 
        class="progress-bar" 
        :style="{ width: value + '%', backgroundColor: color }"
      ></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: Number,
    default: 0
  },
  color: {
    type: String,
    default: '#667eea'
  },
  icon: {
    type: String,
    default: '⭐'
  }
})
</script>

<style scoped>
.stat-bar {
  margin-bottom: 15px;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.stat-icon {
  font-size: 1.2rem;
  margin-right: 8px;
}

.stat-label {
  flex: 1;
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
}

.stat-value {
  font-weight: bold;
  color: #666;
  font-size: 0.9rem;
}

.progress-container {
  height: 12px;
  background: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-bar {
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s ease-out;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>
