<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router    = useRouter()
const route     = useRoute()
const authStore = useAuthStore()

const form = ref({
  name:             '',
  email:            '',
  password:         '',
  invitation_token: route.query.token || null,
})

async function onSubmit() {
  const ok = await authStore.register(form.value)
  if (ok) router.push('/items')
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-accent p-4">
    <div class="w-full max-w-sm">
      <div class="text-center mb-8">
        <div class="text-5xl mb-3">🛒</div>
        <h1 class="text-2xl font-bold text-white">家庭購物清單</h1>
      </div>

      <div class="card">
        <h2 class="text-lg font-semibold text-gray-900 mb-1">建立帳號</h2>
        <p v-if="form.invitation_token" class="text-sm text-green-600 mb-4">🎉 透過邀請連結加入</p>

        <div v-if="authStore.error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
          {{ authStore.error }}
        </div>

        <form @submit.prevent="onSubmit" class="space-y-4">
          <div>
            <label class="label">姓名</label>
            <input v-model="form.name" type="text" required class="input" placeholder="王小明" />
          </div>
          <div>
            <label class="label">Email</label>
            <input v-model="form.email" type="email" required class="input" placeholder="you@example.com" />
          </div>
          <div>
            <label class="label">密碼 <span class="text-gray-400 text-xs">（至少 8 個字元）</span></label>
            <input v-model="form.password" type="password" required minlength="8" class="input" placeholder="••••••••" />
          </div>
          <button type="submit" class="btn-primary w-full" :disabled="authStore.loading">
            <span v-if="authStore.loading">建立中…</span>
            <span v-else>建立帳號</span>
          </button>
        </form>

        <p class="text-center text-sm text-gray-500 mt-6">
          已有帳號？
          <RouterLink to="/login" class="text-primary-600 font-medium hover:underline">立即登入</RouterLink>
        </p>
      </div>
    </div>
  </div>
</template>
