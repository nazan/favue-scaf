<template>
  <div class="page">
    <div class="card">
      <h1>Infrastructure proof</h1>
      <p class="lead">
        This view uses your JWT, opens WebSockets to <code>user-&lt;id&gt;</code> and <code>public</code>, then
        enqueues a worker job. The protected API only accepts requests with a valid Bearer token.
      </p>

      <div v-if="user" class="user-line">
        Signed in as <strong>{{ user.username }}</strong> (id {{ user.id }}) —
        email {{ user.email_verified ? 'verified' : 'not verified' }}
      </div>
      <p v-else class="err">Could not load user — try logging in again.</p>

      <div class="actions">
        <button type="button" class="btn primary" :disabled="!user || jobLoading" @click="runJob">
          {{ jobLoading ? 'Enqueuing…' : 'Call protected route (queue → user WS)' }}
        </button>
      </div>
      <p v-if="jobResult" class="ok">API: {{ jobResult }}</p>
      <p v-if="jobError" class="err">{{ jobError }}</p>

      <h2>WebSocket log</h2>
      <p class="hint">Scheduler fires a <code>public</code> beacon about every 5s (see core-cron in compose). Worker message appears after you run the job.</p>
      <div class="ws-log" ref="logBox">
        <div v-for="(line, i) in logLines" :key="i" class="line">{{ line }}</div>
        <div v-if="!logLines.length" class="empty">Waiting for messages…</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { getWsBaseUrl } from '../config'
import { getMe, getStoredToken, runInfraSecureJob } from '../services/api'
import { userChannel, PUBLIC_CHANNEL } from '../utils/infraTopic'

const user = ref(null)
const logLines = ref([])
const jobLoading = ref(false)
const jobResult = ref(null)
const jobError = ref(null)
const logBox = ref(null)

let ws = null

function appendLog(line) {
  const t = new Date().toISOString()
  logLines.value = [...logLines.value.slice(-200), `${t} ${line}`]
  nextTick(() => {
    const el = logBox.value
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  })
}

function connectWebSocket() {
  const token = getStoredToken()
  if (!token) {
    appendLog('No token; cannot open WebSocket')
    return
  }
  if (ws) {
    try {
      ws.close()
    } catch (e) { /* ignore */ }
    ws = null
  }
  const base = getWsBaseUrl()
  const q = new URLSearchParams({ token })
  const url = `${base}/api/v1/ws/notifications?${q.toString()}`
  appendLog(`Connecting WS…`)
  const socket = new WebSocket(url)
  ws = socket
  socket.onopen = () => {
    appendLog('WebSocket open')
  }
  socket.onmessage = (ev) => {
    appendLog(`message: ${ev.data}`)
  }
  socket.onerror = () => {
    appendLog('WebSocket error')
  }
  socket.onclose = (ev) => {
    appendLog(`WebSocket closed (code ${ev.code})`)
  }
  return new Promise((resolve) => {
    if (socket.readyState === 1) {
      resolve()
      return
    }
    socket.addEventListener('open', () => resolve(), { once: true })
  })
}

function subscribeChannels(uid) {
  if (!ws || ws.readyState !== 1) {
    return
  }
  const ut = userChannel(uid)
  ws.send(JSON.stringify({ op: 'subscribe', topic: ut }))
  ws.send(JSON.stringify({ op: 'subscribe', topic: PUBLIC_CHANNEL }))
  appendLog(`Subscribed: ${ut}, ${PUBLIC_CHANNEL}`)
}

async function runJob() {
  jobResult.value = null
  jobError.value = null
  jobLoading.value = true
  try {
    const data = await runInfraSecureJob()
    jobResult.value = JSON.stringify(data)
  } catch (e) {
    jobError.value = e.message
  } finally {
    jobLoading.value = false
  }
}

onMounted(async () => {
  try {
    user.value = await getMe()
  } catch (e) {
    appendLog(`GET /api/auth/me failed: ${e.message}`)
    return
  }
  if (!user.value) {
    return
  }
  await connectWebSocket()
  subscribeChannels(user.value.id)
})

onUnmounted(() => {
  if (ws) {
    try {
      ws.close()
    } catch (e) { /* ignore */ }
    ws = null
  }
})
</script>

<style scoped>
.page { padding: 1.5rem 1rem 3rem; max-width: 720px; margin: 0 auto; }
.card {
  background: #fff; border-radius: 8px; padding: 1.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  border: 1px solid #e4e4e7;
}
h1 { font-size: 1.5rem; margin-bottom: 0.5rem; }
h2 { font-size: 1.1rem; margin: 1.5rem 0 0.5rem; }
.lead { color: #3f3f46; line-height: 1.5; margin-bottom: 1rem; font-size: 0.95rem; }
code { font-size: 0.85em; background: #f4f4f5; padding: 0.1em 0.35em; border-radius: 4px; }
.user-line { margin-bottom: 1rem; font-size: 0.95rem; }
.actions { margin: 1rem 0; }
.btn {
  padding: 0.55rem 1rem; border: none; border-radius: 6px; font-size: 0.95rem; cursor: pointer; color: #fff;
  background: #4f46e5;
}
.btn:disabled { opacity: 0.6; cursor: not-allowed; }
.ok { color: #166534; font-size: 0.9rem; margin-top: 0.5rem; word-break: break-all; }
.err { color: #b91c1c; font-size: 0.9rem; }
.hint { color: #71717a; font-size: 0.88rem; margin-bottom: 0.5rem; }
.ws-log {
  min-height: 200px; max-height: 360px; overflow: auto; background: #18181b; color: #e4e4e7; font-size: 0.8rem;
  padding: 0.75rem; border-radius: 6px; font-family: ui-monospace, monospace;
}
.line { white-space: pre-wrap; margin-bottom: 0.3rem; }
.empty { color: #71717a; }
</style>
