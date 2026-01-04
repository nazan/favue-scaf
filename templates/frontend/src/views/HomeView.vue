<template>
  <div class="home">
    <div class="container">
      <h1>Welcome to ${PROJECT_NAME}</h1>
      <div class="card">
        <h2>Database Connection Test</h2>
        <div v-if="loading" class="status loading">Loading...</div>
        <div v-else-if="error" class="status error">Error: {{ error }}</div>
        <div v-else-if="dbVersion" class="status success">
          <p><strong>Database Version:</strong> {{ dbVersion.version }}</p>
          <p><strong>Status:</strong> {{ dbVersion.status }}</p>
        </div>
        <button @click="fetchVersion" :disabled="loading" class="btn">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getDatabaseVersion } from '../services/api'

const dbVersion = ref(null)
const loading = ref(false)
const error = ref(null)

async function fetchVersion() {
  loading.value = true
  error.value = null
  try {
    dbVersion.value = await getDatabaseVersion()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchVersion()
})
</script>

<style scoped>
.home {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

h1 {
  color: #333;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #555;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.status {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.status.loading {
  background: #e3f2fd;
  color: #1976d2;
}

.status.error {
  background: #ffebee;
  color: #c62828;
}

.status.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.status.success p {
  margin: 0.5rem 0;
}

.btn {
  background: #1976d2;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.btn:hover:not(:disabled) {
  background: #1565c0;
}

.btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>

