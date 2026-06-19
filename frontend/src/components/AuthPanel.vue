<template>
  <div class="auth-panel">
    <template v-if="user">
      <div class="user-pill">
        <span class="user-avatar">{{ avatarText }}</span>
        <span class="user-name">{{ user.nickname || user.username }}</span>
      </div>

      <button type="button" class="mini-btn" @click="openRecords">
        我的记录
      </button>

      <button type="button" class="mini-btn danger" @click="logout">
        退出
      </button>
    </template>

    <template v-else>
      <span class="guest-label">游客模式</span>

      <button type="button" class="mini-btn" @click="openAuth('login')">
        登录
      </button>

      <button type="button" class="mini-btn primary" @click="openAuth('register')">
        注册
      </button>
    </template>
  </div>

  <div v-if="authDialogVisible" class="auth-dialog-mask" @click.self="closeAuthDialog">
    <div class="auth-dialog">
      <div class="dialog-header">
        <h3>{{ mode === 'login' ? '登录账号' : '注册账号' }}</h3>
        <button type="button" @click="closeAuthDialog">×</button>
      </div>

      <div class="dialog-tabs">
        <button
          type="button"
          :class="{ active: mode === 'login' }"
          @click="switchMode('login')"
        >
          登录
        </button>
        <button
          type="button"
          :class="{ active: mode === 'register' }"
          @click="switchMode('register')"
        >
          注册
        </button>
      </div>

      <div class="dialog-form">
        <input
          v-model.trim="form.username"
          placeholder="账号"
          autocomplete="username"
          @keyup.enter="submitAuth"
        />

        <input
          v-model="form.password"
          type="password"
          placeholder="密码，至少 6 位"
          autocomplete="current-password"
          @keyup.enter="submitAuth"
        />

        <input
          v-if="mode === 'register'"
          v-model.trim="form.nickname"
          placeholder="昵称，可不填"
          autocomplete="nickname"
          @keyup.enter="submitAuth"
        />

        <button type="button" class="submit-btn" :disabled="loading" @click="submitAuth">
          {{ loading ? '处理中...' : mode === 'login' ? '登录' : '注册' }}
        </button>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      </div>
    </div>
  </div>

  <div v-if="recordsVisible" class="records-mask" @click.self="closeRecords">
    <div class="records-panel">
      <div class="records-header">
        <div>
          <h3>我的使用记录</h3>
          <p>当前账号：{{ user?.nickname || user?.username }}</p>
        </div>
        <button type="button" @click="closeRecords">×</button>
      </div>

      <div class="records-filter">
        <button
          v-for="item in recordFilters"
          :key="item.value"
          type="button"
          :class="{ active: activeRecordType === item.value }"
          @click="changeRecordType(item.value)"
        >
          {{ item.label }}
        </button>
      </div>

      <div v-if="recordsLoading" class="records-empty">
        正在加载记录...
      </div>

      <div v-else-if="records.length === 0" class="records-empty">
        暂无记录。登录后使用智能助手、搜索、路线规划或查看景点，会自动保存在这里。
      </div>

      <div v-else class="records-list">
        <div v-for="record in records" :key="record.id" class="record-item">
          <div class="record-top">
            <span class="record-type">{{ getRecordTypeLabel(record.record_type) }}</span>
            <span class="record-time">{{ formatDateTime(record.created_at) }}</span>
          </div>

          <strong>{{ record.title || '未命名记录' }}</strong>

          <p>{{ getRecordSummary(record) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import {
  clearAuth,
  getStoredUser,
  loadUserRecords,
  loginUser,
  onAuthChanged,
  registerUser
} from '../utils/auth'

const user = ref(getStoredUser())
const authDialogVisible = ref(false)
const recordsVisible = ref(false)
const mode = ref('login')
const loading = ref(false)
const recordsLoading = ref(false)
const errorMessage = ref('')
const records = ref([])
const activeRecordType = ref('')

const form = reactive({
  username: '',
  password: '',
  nickname: ''
})

const recordFilters = [
  { value: '', label: '全部' },
  { value: 'assistant_chat', label: '智能问答' },
  { value: 'online_search', label: '在线搜索' },
  { value: 'route_plan', label: '路线规划' },
  { value: 'poi_view', label: '景点查看' }
]

const avatarText = computed(() => {
  const name = user.value?.nickname || user.value?.username || 'U'
  return name.slice(0, 1).toUpperCase()
})

let removeAuthListener = null

onMounted(() => {
  removeAuthListener = onAuthChanged(nextUser => {
    user.value = nextUser
    if (!nextUser) {
      recordsVisible.value = false
      records.value = []
    }
  })
})

onUnmounted(() => {
  if (removeAuthListener) removeAuthListener()
})

function resetForm() {
  form.username = ''
  form.password = ''
  form.nickname = ''
  errorMessage.value = ''
}

function openAuth(nextMode = 'login') {
  mode.value = nextMode
  resetForm()
  authDialogVisible.value = true
}

function closeAuthDialog() {
  authDialogVisible.value = false
  errorMessage.value = ''
}

function switchMode(nextMode) {
  mode.value = nextMode
  errorMessage.value = ''
}

async function submitAuth() {
  errorMessage.value = ''

  if (!form.username || !form.password) {
    errorMessage.value = '请输入账号和密码'
    return
  }

  if (form.username.length < 3) {
    errorMessage.value = '账号至少需要 3 位'
    return
  }

  if (form.password.length < 6) {
    errorMessage.value = '密码至少需要 6 位'
    return
  }

  loading.value = true

  try {
    const data = mode.value === 'login'
      ? await loginUser(form)
      : await registerUser(form)

    user.value = data.user
    closeAuthDialog()
  } catch (error) {
    errorMessage.value = error.message || '操作失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

function logout() {
  clearAuth()
  user.value = null
}

async function openRecords() {
  recordsVisible.value = true
  await refreshRecords()
}

function closeRecords() {
  recordsVisible.value = false
}

async function changeRecordType(type) {
  activeRecordType.value = type
  await refreshRecords()
}

async function refreshRecords() {
  if (!user.value) return

  recordsLoading.value = true

  try {
    records.value = await loadUserRecords({
      record_type: activeRecordType.value,
      limit: 50
    })
  } catch (error) {
    records.value = []
    console.warn('读取用户记录失败：', error)
  } finally {
    recordsLoading.value = false
  }
}

function getRecordTypeLabel(type) {
  const match = recordFilters.find(item => item.value === type)
  return match ? match.label : type || '记录'
}

function formatDateTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  const pad = number => String(number).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function getRecordSummary(record) {
  const content = record.content || {}

  if (record.record_type === 'assistant_chat') {
    return content.answer || content.question || '智能助手问答记录'
  }

  if (record.record_type === 'online_search') {
    return `关键词：${content.keyword || record.title || ''}，结果数：${content.result_count ?? 0}`
  }

  if (record.record_type === 'route_plan') {
    const startName = content.start?.name || '起点'
    const endName = content.end?.name || '终点'
    const modeText = content.mode === 'walking' ? '步行' : content.mode === 'driving' ? '驾车' : content.mode || ''
    const distance = content.summary?.distanceText || ''
    return `${startName} → ${endName}${modeText ? `，${modeText}` : ''}${distance ? `，${distance}` : ''}`
  }

  if (record.record_type === 'poi_view') {
    return content.poi?.address || content.poi?.description || content.poi?.type || '景点查看记录'
  }

  return JSON.stringify(content).slice(0, 120)
}
</script>

<style scoped>
.auth-panel {
  position: fixed;
  left: 420px;
  top: calc(30px + env(safe-area-inset-top));
  right: auto;
  bottom: auto;
  z-index: 2600;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(226, 232, 240, 0.95);
  border-radius: 999px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.16);
  backdrop-filter: blur(8px);
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.user-avatar {
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #2f80ed;
  color: #fff;
  font-weight: 700;
}

.user-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #1f2937;
  font-size: 13px;
  font-weight: 700;
}

.guest-label {
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.mini-btn {
  height: 30px;
  padding: 0 10px;
  border: none;
  border-radius: 999px;
  background: #eef2f7;
  color: #1f2937;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.mini-btn.primary {
  background: #2f80ed;
  color: #fff;
}

.mini-btn.danger {
  background: #fee2e2;
  color: #dc2626;
}

.auth-dialog-mask,
.records-mask {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  background: rgba(15, 23, 42, 0.45);
  box-sizing: border-box;
}

.auth-dialog,
.records-panel {
  width: min(92vw, 420px);
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 22px 70px rgba(15, 23, 42, 0.28);
  overflow: hidden;
}

.dialog-header,
.records-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px;
  border-bottom: 1px solid #eef2f7;
}

.dialog-header h3,
.records-header h3 {
  margin: 0;
  color: #111827;
  font-size: 18px;
}

.records-header p {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 13px;
}

.dialog-header button,
.records-header button {
  width: 34px;
  height: 34px;
  border: none;
  border-radius: 50%;
  background: #f1f5f9;
  color: #334155;
  font-size: 22px;
  cursor: pointer;
}

.dialog-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 16px 18px 0;
  padding: 5px;
  background: #f1f5f9;
  border-radius: 14px;
}

.dialog-tabs button {
  height: 36px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #64748b;
  font-weight: 700;
  cursor: pointer;
}

.dialog-tabs button.active {
  background: #fff;
  color: #2f80ed;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.dialog-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px 18px 20px;
}

.dialog-form input {
  height: 42px;
  padding: 0 12px;
  border: 1px solid #d8dee9;
  border-radius: 12px;
  outline: none;
  font-size: 14px;
  box-sizing: border-box;
}

.dialog-form input:focus {
  border-color: #2f80ed;
  box-shadow: 0 0 0 3px rgba(47, 128, 237, 0.12);
}

.submit-btn {
  height: 42px;
  border: none;
  border-radius: 12px;
  background: #16a34a;
  color: white;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}

.submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.error-text {
  margin: 0;
  color: #dc2626;
  font-size: 13px;
}

.records-panel {
  width: min(94vw, 680px);
  max-height: min(84vh, 680px);
  display: flex;
  flex-direction: column;
}

.records-filter {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  overflow-x: auto;
  border-bottom: 1px solid #eef2f7;
}

.records-filter button {
  flex: 0 0 auto;
  height: 32px;
  padding: 0 12px;
  border: none;
  border-radius: 999px;
  background: #eef2f7;
  color: #475569;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}

.records-filter button.active {
  background: #2f80ed;
  color: #fff;
}

.records-empty {
  padding: 38px 20px;
  text-align: center;
  color: #64748b;
  font-size: 14px;
}

.records-list {
  padding: 12px 16px 18px;
  overflow-y: auto;
}

.record-item {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  background: #f8fafc;
}

.record-item + .record-item {
  margin-top: 10px;
}

.record-top {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 6px;
}

.record-type {
  color: #2f80ed;
  font-size: 12px;
  font-weight: 700;
}

.record-time {
  color: #94a3b8;
  font-size: 12px;
  white-space: nowrap;
}

.record-item strong {
  display: block;
  color: #111827;
  font-size: 15px;
  margin-bottom: 6px;
}

.record-item p {
  margin: 0;
  color: #475569;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
}

@media (max-width: 768px) {
  .auth-panel {
    left: 12px;
    right: auto;
    top: auto;
    bottom: calc(12px + env(safe-area-inset-bottom));
    max-width: calc(100vw - 84px);
    justify-content: flex-start;
    border-radius: 18px;
    padding: 8px 10px;
  }
  .user-name {
    max-width: 88px;
  }
  .guest-label {
    font-size: 12px;
  }
  .mini-btn {
    padding: 0 8px;
    font-size: 12px;
  }
  .auth-dialog-mask,
  .records-mask {
    align-items: flex-end;
    padding: 0;
  }
  .auth-dialog,
  .records-panel {
    width: 100vw;
    max-height: 88vh;
    border-radius: 20px 20px 0 0;
  }
}
</style>