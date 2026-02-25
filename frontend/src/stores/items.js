import { defineStore } from 'pinia'
import { ref } from 'vue'
import { itemsApi } from '@/api'

export const useItemsStore = defineStore('items', () => {
  const items   = ref([])
  const loading = ref(false)
  const error   = ref(null)

  async function fetchItems() {
    loading.value = true
    try {
      const { data } = await itemsApi.list()
      items.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || '載入失敗'
    } finally {
      loading.value = false
    }
  }

  async function createItem(form) {
    const { data } = await itemsApi.create(form)
    items.value.unshift(data)
    return data
  }

  async function updateItem(id, form) {
    const { data } = await itemsApi.update(id, form)
    const idx = items.value.findIndex(i => i.id === id)
    if (idx !== -1) items.value[idx] = data
    return data
  }

  async function deleteItem(id) {
    await itemsApi.delete(id)
    items.value = items.value.filter(i => i.id !== id)
  }

  async function shareItem(id, shareData) {
    const { data } = await itemsApi.share(id, shareData)
    return data
  }

  return { items, loading, error, fetchItems, createItem, updateItem, deleteItem, shareItem }
})
