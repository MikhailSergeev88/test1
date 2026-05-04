<template>
  <button 
    class="action-button" 
    :class="{ disabled, active }"
    @click="$emit('click')"
    :disabled="disabled"
    :title="tooltip"
  >
    <span class="button-icon">{{ icon }}</span>
    <span class="button-label">{{ label }}</span>
  </button>
</template>

<script setup>
defineProps({
  icon: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  disabled: {
    type: Boolean,
    default: false
  },
  active: {
    type: Boolean,
    default: false
  },
  tooltip: {
    type: String,
    default: ''
  }
})

defineEmits(['click'])
</script>

<style scoped>
.action-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 12px 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 15px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  position: relative;
}

.action-button:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.action-button:active:not(:disabled) {
  transform: translateY(-1px);
}

.action-button.disabled {
  background: linear-gradient(135deg, #b2bec3 0%, #636e72 100%);
  cursor: not-allowed;
  opacity: 0.6;
  box-shadow: none;
}

.action-button.active {
  background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
  }
  50% {
    box-shadow: 0 6px 20px rgba(0, 184, 148, 0.6);
  }
}

.button-icon {
  font-size: 2rem;
  margin-bottom: 5px;
}

.button-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-align: center;
}

/* Tooltip */
.action-button[title]:hover:not(:disabled)::after {
  content: attr(title);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  background: #333;
  color: white;
  padding: 5px 10px;
  border-radius: 8px;
  font-size: 0.75rem;
  white-space: nowrap;
  margin-bottom: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  z-index: 10;
}
</style>
