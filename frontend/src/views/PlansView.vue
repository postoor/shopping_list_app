<script setup>
import { ref, computed, onMounted } from "vue";
import { usePlansStore } from "@/stores/plans";
import { useItemsStore } from "@/stores/items";
import { useFriendsStore } from "@/stores/friends";
import PlanCard from "@/components/plans/PlanCard.vue";
import PlanCreateModal from "@/components/plans/PlanCreateModal.vue";
import PlanShareModal from "@/components/plans/PlanShareModal.vue";

const plansStore = usePlansStore();
const itemsStore = useItemsStore();
const friendsStore = useFriendsStore();
const showCreate = ref(false);
const sharePlan = ref(null);
const hideCompleted = ref(true);

const filteredPlans = computed(() => {
  if (hideCompleted.value) {
    return plansStore.plans.filter(p => p.status !== 'completed');
  }
  return plansStore.plans;
});

onMounted(() => {
  plansStore.fetchPlans();
  itemsStore.fetchItems();
  friendsStore.fetchFriends();
});
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">購物計畫</h1>
        <p class="text-sm text-gray-500 mt-0.5">
          選取待購物品，生成一次購物計畫
        </p>
      </div>
      <div class="flex items-center gap-4">
        <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
          <input type="checkbox" v-model="hideCompleted" class="w-4 h-4 rounded border-gray-300 text-primary-500 focus:ring-primary-500" />
          隱藏已完成
        </label>
        <button @click="showCreate = true" class="btn-primary">
          ＋ 建立計畫
        </button>
      </div>
    </div>

    <div v-if="plansStore.loading" class="text-center py-16 text-gray-400">
      載入中…
    </div>
    <div v-else-if="filteredPlans.length === 0" class="text-center py-16">
      <div class="text-4xl mb-3">📋</div>
      <p class="text-gray-500">{{ hideCompleted ? '沒有進行中的計畫' : '尚無購物計畫' }}</p>
    </div>

    <div v-else class="space-y-4">
      <PlanCard
        v-for="plan in filteredPlans"
        :key="plan.id"
        :plan="plan"
        :items="itemsStore.items"
        @toggle="
          ({ planId, piId, done }) =>
            plansStore.togglePlanItem(planId, piId, done)
        "
        @complete="plansStore.completePlan(plan.id)"
        @delete="plansStore.deletePlan(plan.id)"
        @share="sharePlan = plan"
      />
    </div>

    <PlanCreateModal
      v-if="showCreate"
      :pending-items="itemsStore.items.filter((i) => i.status === 'pending')"
      @save="
        async (form) => {
          await plansStore.createPlan(form);
          showCreate = false;
        }
      "
      @cancel="showCreate = false"
    />

    <PlanShareModal
      v-if="sharePlan"
      :plan="sharePlan"
      :friends="friendsStore.friends"
      @close="sharePlan = null"
    />
  </div>
</template>
