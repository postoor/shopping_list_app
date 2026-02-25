<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router    = useRouter()
const authStore = useAuthStore()

const form = ref({ email: '', password: '' })

async function onSubmit() {
  const ok = await authStore.login(form.value.email, form.value.password)
  if (ok) router.push('/items')
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-accent p-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="text-5xl mb-3">🛒</div>
        <h1 class="text-2xl font-bold text-white">家庭購物清單</h1>
        <p class="text-white/80 text-sm mt-1">協作管理您的家庭採購</p>
      </div>

      <div class="card">
        <h2 class="text-lg font-semibold text-gray-900 mb-6">登入帳號</h2>

        <div v-if="authStore.error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
          {{ authStore.error }}
        </div>

        <form @submit.prevent="onSubmit" class="space-y-4">
          <div>
            <label class="label">Email</label>
            <input v-model="form.email" type="email" required class="input" placeholder="you@example.com" />
          </div>
          <div>
            <label class="label">密碼</label>
            <input v-model="form.password" type="password" required class="input" placeholder="••••••••" />
          </div>
          <button type="submit" class="btn-primary w-full" :disabled="authStore.loading">
            <span v-if="authStore.loading">登入中…</span>
            <span v-else>登入</span>
          </button>
        </form>

        <p class="text-center text-sm text-gray-500 mt-6">
          還沒有帳號？
          <RouterLink to="/register" class="text-primary-600 font-medium hover:underline">立即註冊</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
