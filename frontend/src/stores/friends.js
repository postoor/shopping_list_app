import { defineStore } from 'pinia'
import { ref } from 'vue'
import { friendsApi } from '@/api'

export const useFriendsStore = defineStore('friends', () => {
  const friends     = ref([])
  const invitations = ref([])
  const loading     = ref(false)
  const error       = ref(null)

  async function fetchFriends() {
    loading.value = true
    try {
      const { data } = await friendsApi.list()
      friends.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || '載入失敗'
    } finally {
      loading.value = false
    }
  }

  async function fetchInvitations() {
    const { data } = await friendsApi.listInvitations()
    invitations.value = data
  }

  async function invite(email) {
    const { data } = await friendsApi.invite({ invitee_email: email })
    invitations.value.unshift(data)
    return data
  }

  async function removeFriend(id) {
    await friendsApi.remove(id)
    friends.value = friends.value.filter(f => f.id !== id)
  }

  return { friends, invitations, loading, error, fetchFriends, fetchInvitations, invite, removeFriend }
})
