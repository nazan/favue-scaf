<template>
  <div class="home">
    <div class="container">
      <h1>Welcome to ${PROJECT_NAME}</h1>
      <div class="card">
        <h2>Auth &amp; stack demo</h2>
        <p class="blurb">
          <router-link to="/register">Register</router-link> to get a verification link (in development, inspect the
          <strong>core</strong> service logs for the log email transport), open it or visit
          <code>/verify-email?token=…</code>, then use <strong>Infrastructure demo</strong> in the nav after
          <router-link to="/login">log in</router-link>. That flow uses JWT, Taskiq, Redis, WebSockets, and the cron → internal route.
        </p>
        <p class="hint">
          Best experience: use the HTTP gateway (e.g. <code>http://localhost</code> with <code>GATEWAY_PORT=80</code>) so API, Vite, and WebSockets share one origin.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
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

.blurb { color: #3f3f46; line-height: 1.5; margin-bottom: 0.75rem; }
.hint { color: #71717a; font-size: 0.9rem; line-height: 1.4; }
.hint code { background: #f4f4f5; padding: 0.1em 0.3em; border-radius: 4px; }
</style>

