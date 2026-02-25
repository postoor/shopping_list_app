<script setup>
import { ref, onMounted } from 'vue'
import { usePlansStore } from '@/stores/plans'
import { useItemsStore } from '@/stores/items'
import PlanCard from '@/components/plans/PlanCard.vue'
import PlanCreateModal from '@/components/plans/PlanCreateModal.vue'

const plansStore = usePlansStore()
const itemsStore = useItemsStore()
const showCreate = ref(false)

onMounted(() => {
  plansStore.fetchPlans()
  itemsStore.fetchItems()
})
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">購物計畫</h1>
        <p class="text-sm text-gray-500 mt-0.5">選取待購物品，生成一次購物計畫</p>
      </div>
      <button @click="showCreate = true" class="btn-primary">＋ 建立計畫</button>
    </div>

    <div v-if="plansStore.loading" class="text-center py-16 text-gray-400">載入中…</div>
    <div v-else-if="plansStore.plans.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">📋</div>
      <p class="text-gray-500">尚無購物計畫</p>
    </div>

    <div v-else class="space-y-4">
      <PlanCard
        v-for="plan in plansStore.plans"
        :key="plan.id"
        :plan="plan"
        :items="itemsStore.items"
        @toggle="({ planId, piId, done }) => plansStore.togglePlanItem(planId, piId, done)"
        @complete="plansStore.completePlan(plan.id)"
        @delete="plansStore.deletePlan(plan.id)"
      />
    </div>

    <PlanCreateModal
      v-if="showCreate"
      :pending-items="itemsStore.items.filter(i => i.status === 'pending')"
      @save="async (form) => { await plansStore.createPlan(form); showCreate = false }"
      @cancel="showCreate = false"
    />
  </div>
</template>
