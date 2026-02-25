import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user         = ref(null)
  const accessToken  = ref(localStorage.getItem('access_token'))
  const loading      = ref(false)
  const error        = ref(null)

  const isLoggedIn = computed(() => !!accessToken.value && !!user.value)

  async function fetchMe() {
    try {
      const { data } = await authApi.me()
      user.value = data
    } catch {
      logout()
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value   = null
    try {
      const { data } = await authApi.login({ email, password })
      accessToken.value = data.access_token
      localStorage.setItem('access_token',  data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await fetchMe()
      return true
    } catch (e) {
      error.value = e.response?.data?.detail || '登入失敗'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(form) {
    loading.value = true
    error.value   = null
    try {
      await authApi.register(form)
      return await login(form.email, form.password)
    } catch (e) {
      error.value = e.response?.data?.detail || '註冊失敗'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    user.value        = null
    accessToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return { user, accessToken, loading, error, isLoggedIn, login, register, logout, fetchMe }
})
