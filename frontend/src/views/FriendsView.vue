<script setup>
import { ref, onMounted } from "vue";
import { useFriendsStore } from "@/stores/friends";

const store = useFriendsStore();
const inviteEmail = ref("");
const sending = ref(false);
const message = ref(null);

onMounted(() => {
  store.fetchFriends();
  store.fetchInvitations();
});

async function sendInvite() {
  sending.value = true;
  message.value = null;
  try {
    await store.invite(inviteEmail.value);
    message.value = {
      type: "success",
      text: `邀請已發送至 ${inviteEmail.value}`,
    };
    inviteEmail.value = "";
  } catch (e) {
    message.value = {
      type: "error",
      text: e.response?.data?.detail || "發送失敗",
    };
  } finally {
    sending.value = false;
  }
}

function formatDate(d) {
  return new Date(d).toLocaleDateString("zh-TW");
}

function getInviteLink(token) {
  return `${window.location.origin}/register?token=${token}`;
}

async function copyLink(token) {
  const link = getInviteLink(token);
  try {
    await navigator.clipboard.writeText(link);
    message.value = { type: "success", text: "邀請連結已複製" };
  } catch {
    message.value = { type: "error", text: "複製失敗" };
  }
}
</script>

<template>
  <div>
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">好友管理</h1>
      <p class="text-sm text-gray-500 mt-0.5">邀請家人或朋友一起協作購物清單</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 邀請好友 -->
      <div class="card">
        <h2 class="text-base font-semibold text-gray-900 mb-4">✉️ 邀請好友</h2>

        <div
          v-if="message"
          class="mb-4 p-3 rounded-lg text-sm"
          :class="
            message.type === 'success'
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-red-50 text-red-700 border border-red-200'
          "
        >
          {{ message.text }}
        </div>

        <form @submit.prevent="sendInvite" class="flex gap-2">
          <input
            v-model="inviteEmail"
            type="email"
            required
            class="input"
            placeholder="friend@example.com"
          />
          <button
            type="submit"
            class="btn-primary shrink-0"
            :disabled="sending"
          >
            {{ sending ? "發送中…" : "發送邀請" }}
          </button>
        </form>

        <!-- 邀請記錄 -->
        <div class="mt-5">
          <h3 class="text-sm font-medium text-gray-600 mb-3">已發送的邀請</h3>
          <div
            v-if="store.invitations.length === 0"
            class="text-sm text-gray-400"
          >
            尚無邀請記錄
          </div>
          <ul v-else class="space-y-2">
            <li
              v-for="inv in store.invitations"
              :key="inv.id"
              class="text-sm py-2 border-b border-gray-50 last:border-0"
            >
              <div class="flex items-center justify-between">
                <span class="text-gray-700">{{ inv.invitee_email }}</span>
                <span
                  class="text-xs px-2 py-0.5 rounded-full"
                  :class="
                    inv.is_used
                      ? 'bg-green-100 text-green-700'
                      : 'bg-yellow-100 text-yellow-700'
                  "
                >
                  {{ inv.is_used ? "已接受" : "待接受" }}
                </span>
              </div>
              <div v-if="!inv.is_used" class="mt-2 flex items-center gap-2">
                <input
                  :value="getInviteLink(inv.token)"
                  readonly
                  class="input text-xs flex-1 bg-gray-50"
                />
                <button
                  @click="copyLink(inv.token)"
                  class="text-xs text-primary-600 hover:text-primary-700 px-2 py-1 rounded hover:bg-primary-50 transition"
                >
                  複製連結
                </button>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- 好友清單 -->
      <div class="card">
        <h2 class="text-base font-semibold text-gray-900 mb-4">
          👥 好友清單（{{ store.friends.length }}）
        </h2>
        <div v-if="store.loading" class="text-sm text-gray-400">載入中…</div>
        <div
          v-else-if="store.friends.length === 0"
          class="text-center py-8 text-gray-400"
        >
          <div class="text-3xl mb-2">👥</div>
          <p class="text-sm">尚無好友，發送邀請開始協作吧！</p>
        </div>
        <ul v-else class="space-y-2">
          <li
            v-for="friend in store.friends"
            :key="friend.id"
            class="flex items-center justify-between p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition"
          >
            <div class="flex items-center gap-3">
              <div
                class="w-9 h-9 rounded-full bg-primary-100 text-primary-700 font-semibold flex items-center justify-center text-sm"
              >
                {{ friend.name.charAt(0) }}
              </div>
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ friend.name }}
                </p>
                <p class="text-xs text-gray-500">{{ friend.email }}</p>
              </div>
            </div>
            <button
              @click="store.removeFriend(friend.id)"
              class="text-xs text-red-500 hover:text-red-700 hover:bg-red-50 px-2 py-1 rounded transition"
            >
              移除
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
