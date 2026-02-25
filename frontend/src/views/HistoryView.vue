<script setup>
import { ref, onMounted } from 'vue'
import { plansApi } from '@/api'

const plans   = ref([])
const records = ref([])
const loading = ref(false)
const selectedPlan = ref(null)

onMounted(async () => {
  loading.value = true
  const { data } = await plansApi.list()
  plans.value = data.filter(p => p.status === 'completed')
  loading.value = false
})

async function loadRecords(plan) {
  selectedPlan.value = plan
  const { data } = await plansApi.records(plan.id)
  records.value = data
}

function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('zh-TW') : '—'
}

function totalCost(recs) {
  return recs.reduce((sum, r) => sum + (parseFloat(r.actual_price) || 0) * r.quantity, 0).toFixed(0)
}
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">購買紀錄</h1>
      <p class="text-sm text-gray-500 mt-0.5">查詢歷次購物計畫的消費明細</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 計畫列表 -->
      <div class="lg:col-span-1">
        <div class="card">
          <h2 class="text-sm font-semibold text-gray-700 mb-3">已完成的計畫</h2>
          <div v-if="loading" class="text-sm text-gray-400">載入中…</div>
          <div v-else-if="plans.length === 0" class="text-sm text-gray-400">尚無已完成計畫</div>
          <ul v-else class="space-y-2">
            <li v-for="plan in plans" :key="plan.id">
              <button
                @click="loadRecords(plan)"
                class="w-full text-left px-3 py-2.5 rounded-lg text-sm transition"
                :class="selectedPlan?.id === plan.id
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'hover:bg-gray-50 text-gray-700'"
              >
                <p class="font-medium">{{ plan.name }}</p>
                <p class="text-xs text-gray-400 mt-0.5">{{ formatDate(plan.completed_at) }} 完成</p>
              </button>
            </li>
          </ul>
        </div>
      </div>

      <!-- 明細 -->
      <div class="lg:col-span-2">
        <div class="card">
          <div v-if="!selectedPlan" class="text-center py-12 text-gray-400">
            <div class="text-3xl mb-2">📊</div>
            <p class="text-sm">選擇左方計畫查看明細</p>
          </div>
          <div v-else>
            <div class="flex items-center justify-between mb-4">
              <h2 class="font-semibold text-gray-900">{{ selectedPlan.name }}</h2>
              <span class="text-sm text-gray-500">共 {{ records.length }} 項・估計 NT$ {{ totalCost(records) }}</span>
            </div>
            <div v-if="records.length === 0" class="text-sm text-gray-400">無購買紀錄</div>
            <table v-else class="w-full text-sm">
              <thead class="bg-gray-50">
                <tr>
                  <th class="text-left px-3 py-2 text-xs text-gray-500 font-medium">物品</th>
                  <th class="text-center px-3 py-2 text-xs text-gray-500 font-medium">數量</th>
                  <th class="text-right px-3 py-2 text-xs text-gray-500 font-medium">單價</th>
                  <th class="text-right px-3 py-2 text-xs text-gray-500 font-medium">小計</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-50">
                <tr v-for="rec in records" :key="rec.id" class="hover:bg-gray-50">
                  <td class="px-3 py-2.5">
                    <p>{{ rec.item_name }}</p>
                    <p v-if="rec.note" class="text-xs text-gray-400">{{ rec.note }}</p>
                  </td>
                  <td class="px-3 py-2.5 text-center text-gray-600">{{ rec.quantity }}</td>
                  <td class="px-3 py-2.5 text-right text-gray-600">
                    {{ rec.actual_price ? `NT$ ${rec.actual_price}` : '—' }}
                  </td>
                  <td class="px-3 py-2.5 text-right font-medium">
                    {{ rec.actual_price ? `NT$ ${(rec.actual_price * rec.quantity).toFixed(0)}` : '—' }}
                  </td>
                </tr>
              </tbody>
              <tfoot class="border-t-2 border-gray-200">
                <tr>
                  <td colspan="3" class="px-3 py-2.5 text-right font-semibold text-gray-700">合計</td>
                  <td class="px-3 py-2.5 text-right font-bold text-primary-600">NT$ {{ totalCost(records) }}</td>
                </tr>
              </tfoot>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
