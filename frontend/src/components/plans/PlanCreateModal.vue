<script setup>
import { ref } from 'vue'

const props = defineProps({
  pendingItems: { type: Array, default: () => [] },
})
const emit = defineEmits(['save', 'cancel'])

const form = ref({
  name:      '',
  exec_date: '',
  item_ids:  [],
})

function toggleItem(id) {
  const idx = form.value.item_ids.indexOf(id)
  if (idx === -1) form.value.item_ids.push(id)
  else            form.value.item_ids.splice(idx, 1)
}

function onSubmit() {
  const payload = { ...form.value }
  if (!payload.exec_date) delete payload.exec_date
  emit('save', payload)
}
</script>

<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-5">📋 建立購物計畫</h2>

        <form @submit.prevent="onSubmit" class="space-y-4">
          <div>
            <label class="label">計畫名稱 <span class="text-red-500">*</span></label>
            <input v-model="form.name" type="text" required class="input" placeholder="例：週末家庭採購" />
          </div>

          <div>
            <label class="label">執行日期</label>
            <input v-model="form.exec_date" type="date" class="input" />
          </div>

          <div>
            <label class="label">加入待購物品（{{ form.item_ids.length }} 項已選）</label>
            <div v-if="pendingItems.length === 0" class="text-sm text-gray-400 py-2">無待購物品</div>
            <div v-else class="max-h-48 overflow-y-auto space-y-2 border border-gray-200 rounded-lg p-3">
              <label
                v-for="item in pendingItems"
                :key="item.id"
                class="flex items-center gap-3 text-sm cursor-pointer hover:bg-gray-50 rounded p-1"
              >
                <input
                  type="checkbox"
                  :checked="form.item_ids.includes(item.id)"
                  @change="toggleItem(item.id)"
                  class="w-4 h-4 accent-primary-500 rounded"
                />
                <span class="flex-1 text-gray-700">{{ item.name }}</span>
                <span class="text-xs text-gray-400">x{{ item.quantity }}</span>
              </label>
            </div>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="$emit('cancel')" class="btn-secondary">取消</button>
            <button type="submit" class="btn-primary">建立計畫</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
