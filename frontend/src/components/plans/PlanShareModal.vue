<script setup>
import { ref, onMounted } from "vue";
import { plansApi } from "@/api";

const props = defineProps({
  plan: { type: Object, required: true },
  friends: { type: Array, default: () => [] },
});
const emit = defineEmits(["close"]);

const shares = ref([]);
const selectedFriend = ref("");
const selectedPermission = ref("view");
const loading = ref(false);

onMounted(async () => {
  const { data } = await plansApi.listShares(props.plan.id);
  shares.value = data;
});

async function addShare() {
  if (!selectedFriend.value) return;
  loading.value = true;
  try {
    const { data } = await plansApi.share(props.plan.id, {
      shared_with: selectedFriend.value,
      permission: selectedPermission.value,
    });
    shares.value.push(data);
    selectedFriend.value = "";
  } catch (e) {
    alert(e.response?.data?.detail || "分享失敗");
  } finally {
    loading.value = false;
  }
}

async function revokeShare(shareId) {
  await plansApi.revokeShare(props.plan.id, shareId);
  shares.value = shares.value.filter((s) => s.id !== shareId);
}

function friendName(userId) {
  return props.friends.find((f) => f.id === userId)?.name || userId.slice(0, 8);
}
</script>

<template>
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
  >
    <div class="bg-white rounded-2xl shadow-xl w-full max-w-md">
      <div class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-lg font-semibold text-gray-900">
            🔗 分享「{{ plan.name }}」
          </h2>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 text-xl leading-none"
          >
            ✕
          </button>
        </div>

        <!-- Add Share -->
        <div class="flex gap-2 mb-5">
          <select v-model="selectedFriend" class="input flex-1">
            <option value="">選擇好友</option>
            <option v-for="f in friends" :key="f.id" :value="f.id">
              {{ f.name }}
            </option>
          </select>
          <select v-model="selectedPermission" class="input w-28">
            <option value="view">僅查看</option>
            <option value="edit">可編輯</option>
          </select>
          <button
            @click="addShare"
            class="btn-primary shrink-0"
            :disabled="!selectedFriend || loading"
          >
            分享
          </button>
        </div>

        <!-- Current Shares -->
        <div>
          <p class="text-xs font-medium text-gray-500 mb-2">已分享對象</p>
          <div v-if="shares.length === 0" class="text-sm text-gray-400">
            尚未分享給任何人
          </div>
          <ul v-else class="space-y-2">
            <li
              v-for="share in shares"
              :key="share.id"
              class="flex items-center justify-between text-sm bg-gray-50 rounded-lg px-3 py-2"
            >
              <span class="text-gray-700">{{
                friendName(share.shared_with)
              }}</span>
              <div class="flex items-center gap-2">
                <span class="text-xs text-gray-400 capitalize">{{
                  share.permission === "view" ? "查看" : "編輯"
                }}</span>
                <button
                  @click="revokeShare(share.id)"
                  class="text-xs text-red-400 hover:text-red-600"
                >
                  撤銷
                </button>
              </div>
            </li>
          </ul>
        </div>

        <div class="mt-5 flex justify-end">
          <button @click="$emit('close')" class="btn-secondary">關閉</button>
        </div>
      </div>
    </div>
  </div>
</template>
