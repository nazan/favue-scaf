<template>
  <div class="page">
    <div v-if="!submitted" class="card">
      <h1>Create an account</h1>
      <p class="hint">Already have an account? <router-link to="/login">Log in</router-link></p>
      <form @submit.prevent="submit">
        <label class="field">
          <span>Username</span>
          <input v-model="username" type="text" required minlength="2" autocomplete="username" />
        </label>
        <label class="field">
          <span>Email</span>
          <input v-model="email" type="email" required autocomplete="email" />
        </label>
        <label class="field">
          <span>Password (min 8 characters)</span>
          <input v-model="password" type="password" required minlength="8" autocomplete="new-password" />
        </label>
        <p v-if="error" class="err">{{ error }}</p>
        <button type="submit" class="btn" :disabled="loading">{{ loading ? 'Creating…' : 'Register' }}</button>
      </form>
    </div>
    <div v-else class="card success">
      <h1>Check your email</h1>
      <p class="body">{{ resultMessage }}</p>
      <p class="hint">
        In development, the email is only written to the <strong>API container logs</strong> (log transport).
        Copy the link from the log or open it from the message below.
      </p>
      <router-link class="btn primary" :to="{ name: 'login', query: { email: regEmail } }">Go to log in</router-link>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { registerUser } from '../services/api'

const username = ref('')
const email = ref('')
const password = ref('')
const error = ref(null)
const loading = ref(false)
const submitted = ref(false)
const resultMessage = ref('')
const regEmail = ref('')

async function submit() {
  error.value = null
  loading.value = true
  try {
    const r = await registerUser({
      username: username.value.trim(),
      email: email.value.trim(),
      password: password.value,
    })
    regEmail.value = r.email
    resultMessage.value = r.message
    submitted.value = true
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page { padding: 2rem 1rem; max-width: 440px; margin: 0 auto; }
.card {
  background: #fff; border-radius: 8px; padding: 2rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid #e4e4e7;
}
.card.success { border-color: #bbf7d0; }
h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
.hint { color: #52525b; font-size: 0.9rem; margin-bottom: 1rem; line-height: 1.4; }
.hint a { color: #2563eb; }
.body { color: #3f3f46; line-height: 1.5; margin-bottom: 1rem; }
.field { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1rem; }
.field span { font-size: 0.85rem; color: #52525b; }
.field input { padding: 0.5rem 0.6rem; border: 1px solid #d4d4d8; border-radius: 6px; font-size: 1rem; }
.btn {
  display: inline-block; text-align: center; text-decoration: none;
  width: 100%; box-sizing: border-box;
  margin-top: 0.5rem; padding: 0.6rem 1rem; border: none; border-radius: 6px;
  background: #0d9488; color: #fff; font-size: 1rem; cursor: pointer;
}
.btn.primary { background: #2563eb; }
.btn:disabled { opacity: 0.7; cursor: not-allowed; }
.err { color: #b91c1c; font-size: 0.9rem; margin-bottom: 0.5rem; }
</style>
