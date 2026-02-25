import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login',    name: 'Login',    component: () => import('@/views/LoginView.vue'),    meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/RegisterView.vue'), meta: { guest: true } },
  {
    path: '/',
    component: () => import('@/views/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '',         name: 'Home',     redirect: '/items' },
      { path: 'items',    name: 'Items',    component: () => import('@/views/ItemsView.vue') },
      { path: 'groups',   name: 'Groups',   component: () => import('@/views/GroupsView.vue') },
      { path: 'plans',    name: 'Plans',    component: () => import('@/views/PlansView.vue') },
      { path: 'friends',  name: 'Friends',  component: () => import('@/views/FriendsView.vue') },
      { path: 'history',  name: 'History',  component: () => import('@/views/HistoryView.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // 載入使用者（有 token 但還沒載入）
  if (auth.accessToken && !auth.user) {
    await auth.fetchMe()
  }

  if (to.meta.requiresAuth && !auth.isLoggedIn) return { name: 'Login' }
  if (to.meta.guest && auth.isLoggedIn)         return { name: 'Items' }
})

export default router
