<script setup>
import { ref, computed } from 'vue'
import { useRouter, RouterView, RouterLink, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router    = useRouter()
const route     = useRoute()
const authStore = useAuthStore()
const sidebarOpen = ref(false)

const navItems = [
  { to: '/items',   label: '購物清單', icon: '🛒' },
  { to: '/plans',   label: '購物計畫', icon: '📋' },
  { to: '/groups',  label: '群組管理', icon: '👨‍👩‍👧' },
  { to: '/friends', label: '好友管理', icon: '👥' },
  { to: '/history', label: '購買紀錄', icon: '📊' },
]

function logout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex">
    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 lg:translate-x-0 lg:static lg:inset-auto"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="px-6 py-5 border-b border-gray-100">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-accent flex items-center justify-center text-white text-lg">
              🛒
            </div>
            <div>
              <p class="font-bold text-gray-900 text-sm">家庭購物清單</p>
              <p class="text-xs text-gray-500">{{ authStore.user?.name }}</p>
            </div>
          </div>
        </div>

        <!-- Nav -->
        <nav class="flex-1 px-4 py-4 space-y-1 overflow-y-auto">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
            :class="route.path.startsWith(item.to)
              ? 'bg-primary-50 text-primary-700'
              : 'text-gray-600 hover:bg-gray-100'"
            @click="sidebarOpen = false"
          >
            <span class="text-lg leading-none">{{ item.icon }}</span>
            {{ item.label }}
          </RouterLink>
        </nav>

        <!-- User Footer -->
        <div class="px-4 py-4 border-t border-gray-100">
          <button
            @click="logout"
            class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-red-600 hover:bg-red-50 transition-colors"
          >
            <span>🚪</span> 登出
          </button>
        </div>
      </div>
    </aside>

    <!-- Overlay -->
    <div
      v-if="sidebarOpen"
      class="fixed inset-0 z-20 bg-black/40 lg:hidden"
      @click="sidebarOpen = false"
    />

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Mobile header -->
      <header class="lg:hidden sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3 flex items-center gap-3">
        <button @click="sidebarOpen = !sidebarOpen" class="p-2 rounded-lg text-gray-600 hover:bg-gray-100">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
        <span class="font-semibold text-gray-900">家庭購物清單</span>
      </header>

      <main class="flex-1 p-6 overflow-auto">
        <RouterView />
      </main>
    </div>
  </div>
</template>
