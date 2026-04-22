import { createRouter, createWebHistory } from 'vue-router'
import { getStoredToken } from '../services/api'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import InfrastructureDemoView from '../views/InfrastructureDemoView.vue'
import VerifyEmailView from '../views/VerifyEmailView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/verify-email', name: 'verify-email', component: VerifyEmailView },
  {
    path: '/infrastructure-demo',
    name: 'infrastructure-demo',
    component: InfrastructureDemoView,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !getStoredToken()) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  next()
})

export default router
