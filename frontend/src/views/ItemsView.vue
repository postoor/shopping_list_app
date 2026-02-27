<script setup>
import { ref, computed, onMounted } from 'vue'
import { useItemsStore } from '@/stores/items'
import { useFriendsStore } from '@/stores/friends'
import ItemCard from '@/components/items/ItemCard.vue'
import ItemForm from '@/components/items/ItemForm.vue'
import ShareModal from '@/components/shared/ShareModal.vue'

const itemsStore   = useItemsStore()
const friendsStore = useFriendsStore()

const showForm    = ref(false)
const editingItem = ref(null)
const sharingItem = ref(null)
const filterStatus   = ref('all')
const filterCategory = ref('all')
const search      = ref('')
const hideCompleted  = ref(true)

onMounted(() => {
  itemsStore.fetchItems()
  friendsStore.fetchFriends()
})

const filteredItems = computed(() => {
  return itemsStore.items.filter(item => {
    const matchStatus   = filterStatus.value   === 'all' || item.status   === filterStatus.value
    const matchCategory = filterCategory.value === 'all' || item.category === filterCategory.value
    const matchSearch   = !search.value || item.name.toLowerCase().includes(search.value.toLowerCase())
    const matchCompleted = !hideCompleted.value || item.status !== 'purchased'
    return matchStatus && matchCategory && matchSearch && matchCompleted
  })
})

function startEdit(item) {
  editingItem.value = item
  showForm.value    = true
}

function startShare(item) {
  sharingItem.value = item
}

async function onSave(form) {
  if (editingItem.value) {
    await itemsStore.updateItem(editingItem.value.id, form)
  } else {
    await itemsStore.createItem(form)
  }
  showForm.value    = false
  editingItem.value = null
}

function onCancel() {
  showForm.value    = false
  editingItem.value = null
}
</script>

<template>
  <div>
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">購物清單</h1>
        <p class="text-sm text-gray-500 mt-0.5">管理所有待購物品</p>
      </div>
      <button @click="showForm = true; editingItem = null" class="btn-primary shrink-0">
        ＋ 新增物品
      </button>
    </div>

    <!-- Filters -->
    <div class="card mb-5">
      <div class="flex flex-wrap items-center gap-3">
        <input v-model="search" class="input max-w-xs" placeholder="🔍 搜尋物品名稱…" />
        <select v-model="filterStatus"   class="input w-auto">
          <option value="all">所有狀態</option>
          <option value="pending">待購</option>
          <option value="shopping">購物中</option>
          <option value="purchased">已購買</option>
        </select>
        <select v-model="filterCategory" class="input w-auto">
          <option value="all">所有分類</option>
          <option value="essential">必需品</option>
          <option value="non_essential">非必需品</option>
        </select>
        <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer ml-auto">
          <input type="checkbox" v-model="hideCompleted" class="w-4 h-4 rounded border-gray-300 text-primary-500 focus:ring-primary-500" />
          隱藏已購買
        </label>
      </div>
    </div>

    <!-- Loading / Empty -->
    <div v-if="itemsStore.loading" class="text-center py-16 text-gray-400">載入中…</div>
    <div v-else-if="filteredItems.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">🛒</div>
      <p class="text-gray-500">尚無物品，點擊「新增物品」開始記錄</p>
    </div>

    <!-- Items Grid -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <ItemCard
        v-for="item in filteredItems"
        :key="item.id"
        :item="item"
        @edit="startEdit"
        @share="startShare"
        @delete="itemsStore.deleteItem(item.id)"
        @status-change="(s) => itemsStore.updateItem(item.id, { status: s })"
      />
    </div>

    <!-- Form Modal -->
    <ItemForm
      v-if="showForm"
      :item="editingItem"
      @save="onSave"
      @cancel="onCancel"
    />

    <!-- Share Modal -->
    <ShareModal
      v-if="sharingItem"
      :item="sharingItem"
      :friends="friendsStore.friends"
      @close="sharingItem = null"
    />
  </div>
</template>
