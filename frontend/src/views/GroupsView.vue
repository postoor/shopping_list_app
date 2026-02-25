<script setup>
import { ref, onMounted } from 'vue'
import { groupsApi } from '@/api'
import { useFriendsStore } from '@/stores/friends'

const friendsStore = useFriendsStore()
const groups   = ref([])
const loading  = ref(false)
const showForm = ref(false)
const newName  = ref('')

onMounted(async () => {
  loading.value = true
  const { data } = await groupsApi.list()
  groups.value  = data
  loading.value = false
  friendsStore.fetchFriends()
})

async function createGroup() {
  if (!newName.value.trim()) return
  const { data } = await groupsApi.create({ name: newName.value })
  groups.value.unshift(data)
  showForm.value = false
  newName.value  = ''
}

async function deleteGroup(id) {
  await groupsApi.delete(id)
  groups.value = groups.value.filter(g => g.id !== id)
}

async function addMember(groupId, userId) {
  const { data } = await groupsApi.addMember(groupId, { user_id: userId, role: 'viewer' })
  const g = groups.value.find(g => g.id === groupId)
  if (g) g.members.push(data)
}

async function removeMember(groupId, userId) {
  await groupsApi.removeMember(groupId, userId)
  const g = groups.value.find(g => g.id === groupId)
  if (g) g.members = g.members.filter(m => m.user_id !== userId)
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">群組管理</h1>
        <p class="text-sm text-gray-500 mt-0.5">建立群組並邀請成員共同管理清單</p>
      </div>
      <button @click="showForm = true" class="btn-primary">＋ 新增群組</button>
    </div>

    <!-- New Group Form -->
    <div v-if="showForm" class="card mb-5">
      <h3 class="font-medium text-gray-900 mb-3">建立新群組</h3>
      <div class="flex gap-2">
        <input v-model="newName" class="input" placeholder="群組名稱（例：家庭採購）" @keyup.enter="createGroup" />
        <button @click="createGroup" class="btn-primary">建立</button>
        <button @click="showForm = false; newName = ''" class="btn-secondary">取消</button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-16 text-gray-400">載入中…</div>
    <div v-else-if="groups.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">👨‍👩‍👧</div>
      <p class="text-gray-500">尚無群組</p>
    </div>

    <div v-else class="space-y-4">
      <div v-for="group in groups" :key="group.id" class="card">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h3 class="font-semibold text-gray-900">{{ group.name }}</h3>
            <p class="text-xs text-gray-400 mt-0.5">{{ group.members.length }} 位成員</p>
          </div>
          <button @click="deleteGroup(group.id)" class="text-xs text-red-500 hover:text-red-700 px-2 py-1 rounded hover:bg-red-50 transition">
            刪除群組
          </button>
        </div>

        <!-- Members -->
        <div class="space-y-2 mb-4">
          <div v-for="member in group.members" :key="member.user_id"
            class="flex items-center justify-between text-sm py-1.5 border-b border-gray-50 last:border-0">
            <span class="text-gray-700">{{ member.user_id }}</span>
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-400 capitalize">{{ member.role }}</span>
              <button @click="removeMember(group.id, member.user_id)"
                class="text-xs text-red-400 hover:text-red-600">移除</button>
            </div>
          </div>
        </div>

        <!-- Add Member -->
        <div class="pt-3 border-t border-gray-100">
          <p class="text-xs font-medium text-gray-500 mb-2">新增好友至群組：</p>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="friend in friendsStore.friends.filter(f => !group.members.find(m => m.user_id === f.id))"
              :key="friend.id"
              @click="addMember(group.id, friend.id)"
              class="text-xs px-3 py-1.5 rounded-full border border-primary-200 text-primary-600 hover:bg-primary-50 transition"
            >
              ＋ {{ friend.name }}
            </button>
            <span v-if="friendsStore.friends.filter(f => !group.members.find(m => m.user_id === f.id)).length === 0"
              class="text-xs text-gray-400">所有好友已加入</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
