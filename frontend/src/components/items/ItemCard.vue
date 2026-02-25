<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
})

const emit = defineEmits(['edit', 'share', 'delete', 'status-change'])

const statusLabel = { pending: '待購', shopping: '購物中', purchased: '已購買' }
const statusNext  = { pending: 'shopping', shopping: 'purchased', purchased: 'pending' }
const categoryLabel = { essential: '必需品', non_essential: '非必需品' }

const statusClass = computed(() => ({
  pending:   'badge-pending',
  shopping:  'badge-shopping',
  purchased: 'badge-purchased',
}[props.item.status]))

const categoryClass = computed(() => ({
  essential:     'badge-essential',
  non_essential: 'badge-non-essential',
}[props.item.category]))
</script>

<template>
  <div class="card hover:shadow-md transition-shadow group">
    <!-- Header -->
    <div class="flex items-start justify-between mb-3">
      <div class="flex-1 min-w-0 pr-2">
        <h3 class="font-semibold text-gray-900 truncate">{{ item.name }}</h3>
        <p v-if="item.brand_note" class="text-xs text-gray-400 mt-0.5 truncate">{{ item.brand_note }}</p>
      </div>
      <!-- Actions -->
      <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <button @click="$emit('edit', item)" class="p-1.5 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-gray-600 transition" title="編輯">
          ✏️
        </button>
        <button @click="$emit('share', item)" class="p-1.5 rounded-lg hover:bg-blue-50 text-gray-400 hover:text-blue-600 transition" title="分享">
          🔗
        </button>
        <button @click="$emit('delete', item)" class="p-1.5 rounded-lg hover:bg-red-50 text-gray-400 hover:text-red-500 transition" title="刪除">
          🗑️
        </button>
      </div>
    </div>

    <!-- Info -->
    <div class="flex flex-wrap gap-1.5 mb-3">
      <span :class="categoryClass">{{ categoryLabel[item.category] }}</span>
      <span :class="statusClass">{{ statusLabel[item.status] }}</span>
    </div>

    <div class="flex items-center gap-4 text-sm text-gray-600 mb-4">
      <span>數量：<strong>{{ item.quantity }}</strong></span>
      <span v-if="item.est_price">預估：<strong>NT$ {{ item.est_price }}</strong></span>
    </div>

    <p v-if="item.note" class="text-xs text-gray-400 mb-4 line-clamp-2">{{ item.note }}</p>

    <!-- Status Toggle -->
    <button
      @click="$emit('status-change', statusNext[item.status])"
      class="w-full text-sm py-2 rounded-lg border transition"
      :class="{
        'border-yellow-200 text-yellow-700 hover:bg-yellow-50': item.status === 'pending',
        'border-purple-200 text-purple-700 hover:bg-purple-50': item.status === 'shopping',
        'border-green-200 text-green-700 hover:bg-green-50':   item.status === 'purchased',
      }"
    >
      {{ item.status === 'pending' ? '開始購物' : item.status === 'shopping' ? '✓ 標為已購' : '↩ 重設為待購' }}
    </button>
  </div>
</template>
