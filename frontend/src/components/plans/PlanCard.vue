<script setup>
import { computed } from 'vue'

const props = defineProps({
  plan:  { type: Object, required: true },
  items: { type: Array,  default: () => [] },
})
const emit = defineEmits(['toggle', 'complete', 'delete'])

const progress = computed(() => {
  const total = props.plan.plan_items.length
  const done  = props.plan.plan_items.filter(pi => pi.is_done).length
  return { total, done, pct: total ? Math.round(done / total * 100) : 0 }
})

function itemName(itemId) {
  return props.items.find(i => i.id === itemId)?.name || '未知物品'
}

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('zh-TW') : null
}
</script>

<template>
  <div class="card">
    <!-- Header -->
    <div class="flex items-start justify-between mb-3">
      <div>
        <div class="flex items-center gap-2">
          <h3 class="font-semibold text-gray-900">{{ plan.name }}</h3>
          <span class="text-xs px-2 py-0.5 rounded-full font-medium"
            :class="plan.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-purple-100 text-purple-700'">
            {{ plan.status === 'completed' ? '已完成' : '進行中' }}
          </span>
        </div>
        <p class="text-xs text-gray-400 mt-0.5">
          {{ formatDate(plan.exec_date) || '尚未設定執行日期' }}
        </p>
      </div>
      <button v-if="plan.status !== 'completed'" @click="$emit('delete')"
        class="text-xs text-red-400 hover:text-red-600 px-2 py-1 rounded hover:bg-red-50 transition">刪除</button>
    </div>

    <!-- Progress Bar -->
    <div class="mb-4">
      <div class="flex justify-between text-xs text-gray-500 mb-1">
        <span>已勾除 {{ progress.done }} / {{ progress.total }} 項</span>
        <span>{{ progress.pct }}%</span>
      </div>
      <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div class="h-full bg-primary-500 rounded-full transition-all" :style="{ width: progress.pct + '%' }"></div>
      </div>
    </div>

    <!-- Items -->
    <ul class="space-y-2 mb-4">
      <li v-for="pi in plan.plan_items" :key="pi.id"
        class="flex items-center gap-3 text-sm py-1">
        <input
          type="checkbox"
          :checked="pi.is_done"
          :disabled="plan.status === 'completed'"
          @change="$emit('toggle', { planId: plan.id, piId: pi.id, done: !pi.is_done })"
          class="w-4 h-4 rounded accent-primary-500 cursor-pointer"
        />
        <span :class="pi.is_done ? 'line-through text-gray-400' : 'text-gray-700'">
          {{ itemName(pi.item_id) }}
        </span>
      </li>
    </ul>

    <!-- Complete Button -->
    <button
      v-if="plan.status !== 'completed'"
      @click="$emit('complete')"
      :disabled="progress.pct < 100"
      class="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
    >
      ✓ 完成購物並儲存紀錄
    </button>
    <p v-if="plan.status !== 'completed' && progress.pct < 100" class="text-xs text-gray-400 text-center mt-2">
      請先勾除所有物品
    </p>
  </div>
</template>
