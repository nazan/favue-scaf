<template>
  <div id="app" class="app-root">
    <header class="top-nav">
      <div class="nav-inner">
        <router-link to="/" class="brand">${PROJECT_NAME}</router-link>
        <nav class="nav-links">
          <router-link to="/">Home</router-link>
          <router-link to="/infrastructure-demo">Infrastructure demo</router-link>
          <router-link v-if="!isAuthed" to="/login">Log in</router-link>
          <router-link v-if="!isAuthed" to="/register">Register</router-link>
          <a v-else href="#" @click.prevent="logout">Log out</a>
        </nav>
      </div>
    </header>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getStoredToken, clearStoredToken } from './services/api'

const router = useRouter()
const isAuthed = ref(!!getStoredToken())

onMounted(() => {
  isAuthed.value = !!getStoredToken()
})

watch(
  () => router.currentRoute.value.fullPath,
  () => {
    isAuthed.value = !!getStoredToken()
  }
)

function logout() {
  clearStoredToken()
  isAuthed.value = false
  router.push({ name: 'home' })
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: #f4f4f5;
  color: #1a1a1a;
}

#app, .app-root {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-nav {
  background: #fff;
  border-bottom: 1px solid #e4e4e7;
  padding: 0.75rem 1.25rem;
}

.nav-inner {
  max-width: 960px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.brand {
  font-weight: 600;
  text-decoration: none;
  color: #18181b;
}

.nav-links {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.nav-links a {
  color: #3f3f46;
  text-decoration: none;
  font-size: 0.95rem;
}

.nav-links a:hover {
  color: #0f172a;
}

.main-content {
  flex: 1;
}
</style>
