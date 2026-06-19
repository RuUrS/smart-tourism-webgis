<template>
  <div class="auth-entry-page">
    <div class="auth-entry-card">
      <div class="system-logo">🗺️</div>

      <h1>智慧旅游 WebGIS 系统</h1>
      <p class="subtitle">请选择进入方式</p>

      <button class="guest-btn" type="button" @click="enterAsGuest">
        游客进入系统
      </button>

      <div class="divider">
        <span>或使用账号登录</span>
      </div>

      <div class="tabs">
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

      <div class="form-box">
        <input
          v-model.trim="form.username"
          placeholder="请输入账号"
          autocomplete="username"
          @keyup.enter="submitAuth"
        />

        <input
          v-model="form.password"
          type="password"
          placeholder="请输入密码，至少 6 位"
          autocomplete="current-password"
          @keyup.enter="submitAuth"
        />

        <input
          v-if="mode === 'register'"
          v-model.trim="form.nickname"
          placeholder="请输入昵称，可不填"
          autocomplete="nickname"
          @keyup.enter="submitAuth"
        />

        <button class="submit-btn" type="button" :disabled="loading" @click="submitAuth">
          {{ loading ? '处理中...' : mode === 'login' ? '登录并进入' : '注册并进入' }}
        </button>

        <p v-if="errorMessage" class="error-text">
          {{ errorMessage }}
        </p>
      </div>

      <p class="tip-text">
        游客模式可以直接使用地图、搜索、路线规划和智能助手；登录后可保存个人使用记录。
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { enterGuestMode, loginUser, registerUser } from '../utils/auth'

const emit = defineEmits(['guest-enter', 'auth-enter'])

const mode = ref('login')
const loading = ref(false)
const errorMessage = ref('')

const form = reactive({
  username: '',
  password: '',
  nickname: ''
})

function switchMode(nextMode) {
  mode.value = nextMode
  errorMessage.value = ''
}

function enterAsGuest() {
  enterGuestMode()
  emit('guest-enter')
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

    emit('auth-enter', data.user)
  } catch (error) {
    errorMessage.value = error.message || '操作失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-entry-page {
  width: 100vw;
  height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background:
    radial-gradient(circle at top left, rgba(47, 128, 237, 0.18), transparent 36%),
    linear-gradient(135deg, #eaf3ff 0%, #f6f8fb 48%, #eef7f0 100%);
  box-sizing: border-box;
}

.auth-entry-card {
  width: 100%;
  max-width: 420px;
  padding: 34px 28px 28px;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 24px;
  box-shadow: 0 18px 50px rgba(28, 45, 75, 0.18);
  text-align: center;
  box-sizing: border-box;
}

.system-logo {
  width: 68px;
  height: 68px;
  margin: 0 auto 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef5ff;
  border-radius: 22px;
  font-size: 34px;
}

h1 {
  margin: 0;
  font-size: 24px;
  color: #1f2d3d;
}

.subtitle {
  margin: 10px 0 22px;
  color: #6b7280;
  font-size: 14px;
}

.guest-btn,
.submit-btn {
  width: 100%;
  height: 46px;
  border: none;
  border-radius: 14px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.guest-btn {
  background: #2f80ed;
}

.submit-btn {
  height: 44px;
  background: #16a34a;
}

.submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.divider {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 24px 0 16px;
  color: #9ca3af;
  font-size: 13px;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e5e7eb;
}

.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 14px;
  padding: 5px;
  background: #f1f5f9;
  border-radius: 14px;
}

.tabs button {
  height: 36px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #64748b;
  font-weight: 700;
  cursor: pointer;
}

.tabs button.active {
  background: white;
  color: #2f80ed;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
}

.form-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-box input {
  height: 44px;
  padding: 0 14px;
  border: 1px solid #d8dee9;
  border-radius: 12px;
  outline: none;
  font-size: 15px;
  box-sizing: border-box;
}

.form-box input:focus {
  border-color: #2f80ed;
  box-shadow: 0 0 0 3px rgba(47, 128, 237, 0.12);
}

.error-text {
  margin: 2px 0 0;
  color: #dc2626;
  font-size: 13px;
}

.tip-text {
  margin: 18px 0 0;
  color: #7b8794;
  font-size: 13px;
  line-height: 1.6;
}

@media (max-width: 480px) {
  .auth-entry-page {
    padding: 16px;
    align-items: stretch;
  }

  .auth-entry-card {
    margin: auto 0;
    padding: 28px 20px 24px;
    border-radius: 22px;
  }

  h1 {
    font-size: 21px;
  }
}
</style>
