<template>
  <div class="page">
    <div class="card">
      <h1>Email verification</h1>
      <p v-if="status === 'pending'" class="muted">Verifying your link…</p>
      <p v-else-if="status === 'ok'" class="ok">{{ message }}</p>
      <p v-else class="err">{{ error }}</p>
      <p class="actions">
        <router-link to="/login" class="link">Log in</router-link>
        ·
        <router-link to="/" class="link">Home</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { verifyEmailToken } from '../services/api'

const route = useRoute()
const status = ref('pending')
const message = ref('')
const error = ref('')

onMounted(async () => {
  const raw = route.query.token
  const token = typeof raw === 'string' ? raw : (Array.isArray(raw) ? raw[0] : '')
  if (!token) {
    status.value = 'err'
    error.value = 'Missing verification token in the link.'
    return
  }
  try {
    const r = await verifyEmailToken(token)
    message.value = r.message || 'Email verified successfully.'
    status.value = 'ok'
  } catch (e) {
    status.value = 'err'
    error.value = e.message || 'Verification failed'
  }
})
</script>

<style scoped>
.page { padding: 2rem 1rem; max-width: 480px; margin: 0 auto; }
.card {
  background: #fff; border-radius: 8px; padding: 2rem; border: 1px solid #e4e4e7;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
h1 { font-size: 1.4rem; margin-bottom: 0.75rem; }
.muted { color: #71717a; }
.ok { color: #166534; }
.err { color: #b91c1c; }
.actions { margin-top: 1.25rem; }
.link { color: #2563eb; text-decoration: none; }
.link:hover { text-decoration: underline; }
</style>
