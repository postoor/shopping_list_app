<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  item: { type: Object, default: null },
})
const emit = defineEmits(['save', 'cancel'])

const form = ref({
  name:       '',
  quantity:   1,
  est_price:  null,
  category:   'essential',
  status:     'pending',
  brand_note: '',
  note:       '',
  group_id:   null,
})

watch(() => props.item, (val) => {
  if (val) {
    form.value = { ...val }
  } else {
    form.value = { name: '', quantity: 1, est_price: null, category: 'essential', status: 'pending', brand_note: '', note: '', group_id: null }
  }
}, { immediate: true })

function onSubmit() {
  const payload = { ...form.value }
  if (!payload.est_price) delete payload.est_price
  if (!payload.brand_note) delete payload.brand_note
  if (!payload.note) delete payload.note
  emit('save', payload)
}
</script>

<template>
  <!-- Modal Overlay -->
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
      <div class="p-6">
        <h2 class="text-lg font-semibold text-gray-900 mb-5">
          {{ item ? '✏️ 編輯物品' : '＋ 新增物品' }}
        </h2>

        <form @submit.prevent="onSubmit" class="space-y-4">
          <div>
            <label class="label">物品名稱 <span class="text-red-500">*</span></label>
            <input v-model="form.name" type="text" required class="input" placeholder="例：牛奶" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">數量</label>
              <input v-model.number="form.quantity" type="number" min="1" class="input" />
            </div>
            <div>
              <label class="label">預估價格 (NT$)</label>
              <input v-model.number="form.est_price" type="number" min="0" step="0.01" class="input" placeholder="選填" />
            </div>
          </div>

          <div>
            <label class="label">分類</label>
            <select v-model="form.category" class="input">
              <option value="essential">必需品</option>
              <option value="non_essential">非必需品</option>
            </select>
          </div>

          <div>
            <label class="label">廠牌偏好 / 購買參考</label>
            <input v-model="form.brand_note" type="text" class="input" placeholder="例：光泉全脂牛奶 936ml" />
          </div>

          <div>
            <label class="label">備註</label>
            <textarea v-model="form.note" class="input" rows="2" placeholder="其他說明…"></textarea>
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button type="button" @click="$emit('cancel')" class="btn-secondary">取消</button>
            <button type="submit" class="btn-primary">{{ item ? '儲存' : '新增' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
