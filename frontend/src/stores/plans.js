import { defineStore } from 'pinia'
import { ref } from 'vue'
import { plansApi } from '@/api'

export const usePlansStore = defineStore('plans', () => {
  const plans   = ref([])
  const loading = ref(false)
  const error   = ref(null)

  async function fetchPlans() {
    loading.value = true
    try {
      const { data } = await plansApi.list()
      plans.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || '載入失敗'
    } finally {
      loading.value = false
    }
  }

  async function createPlan(form) {
    const { data } = await plansApi.create(form)
    plans.value.unshift(data)
    return data
  }

  async function togglePlanItem(planId, planItemId, isDone) {
    const { data } = await plansApi.toggleItem(planId, planItemId, { is_done: isDone })
    const idx = plans.value.findIndex(p => p.id === planId)
    if (idx !== -1) plans.value[idx] = data
    return data
  }

  async function completePlan(planId) {
    const { data } = await plansApi.complete(planId)
    const idx = plans.value.findIndex(p => p.id === planId)
    if (idx !== -1) plans.value[idx] = data
    return data
  }

  async function deletePlan(id) {
    await plansApi.delete(id)
    plans.value = plans.value.filter(p => p.id !== id)
  }

  return { plans, loading, error, fetchPlans, createPlan, togglePlanItem, completePlan, deletePlan }
})
