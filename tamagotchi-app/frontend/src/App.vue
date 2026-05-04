<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import { usePetStore } from './store/pet'

const petStore = usePetStore()

onMounted(() => {
  petStore.loadPet()
  petStore.startDecayTimer()
})
</script>
