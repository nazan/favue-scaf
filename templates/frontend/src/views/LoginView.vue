<template>
  <div class="page">
    <div class="card">
      <h1>Log in</h1>
      <p class="hint">Use the email and password for your account. First time? <router-link to="/register">Register</router-link></p>
      <form @submit.prevent="submit">
        <label class="field">
          <span>Email</span>
          <input v-model="email" type="email" autocomplete="email" required />
        </label>
        <label class="field">
          <span>Password</span>
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>
        <p v-if="error" class="err">{{ error }}</p>
        <button type="submit" class="btn" :disabled="loading">{{ loading ? 'Signing in…' : 'Log in' }}</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { loginWithPassword, setStoredToken } from '../services/api'

const route = useRoute()
const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref(null)
const loading = ref(false)

onMounted(() => {
  const pre = route.query.email
  if (typeof pre === 'string' && pre.includes('@')) {
    email.value = pre
  }
})

async function submit() {
  error.value = null
  loading.value = true
  try {
    const data = await loginWithPassword(email.value.trim(), password.value)
    setStoredToken(data.access_token)
    const redir = route.query.redirect
    if (typeof redir === 'string' && redir.startsWith('/')) {
      await router.push(redir)
    } else {
      await router.push({ name: 'home' })
    }
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page {
  padding: 2rem 1rem;
  max-width: 440px;
  margin: 0 auto;
}
.card {
  background: #fff;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid #e4e4e7;
}
h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
.hint { color: #52525b; font-size: 0.9rem; margin-bottom: 1.25rem; }
.hint a { color: #2563eb; }
.field { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1rem; }
.field span { font-size: 0.85rem; color: #52525b; }
.field input {
  padding: 0.5rem 0.6rem; border: 1px solid #d4d4d8; border-radius: 6px; font-size: 1rem;
}
.btn {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.6rem 1rem; border: none; border-radius: 6px;
  background: #2563eb; color: #fff; font-size: 1rem; cursor: pointer;
}
.btn:disabled { opacity: 0.7; cursor: not-allowed; }
.err { color: #b91c1c; font-size: 0.9rem; margin-bottom: 0.5rem; }
</style>
