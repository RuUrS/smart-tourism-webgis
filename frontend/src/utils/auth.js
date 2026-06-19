// 登录状态与用户记录工具
// 作用：保存 token、读取当前用户、退出登录、保存用户使用记录。

const TOKEN_KEY = 'smart_tourism_token'
const USER_KEY = 'smart_tourism_user'
const GUEST_KEY = 'smart_tourism_guest_entered'

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function getStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  } catch {
    return null
  }
}

export function isLoggedIn() {
  return Boolean(getAuthToken())
}

export function hasGuestEntered() {
  return sessionStorage.getItem(GUEST_KEY) === '1'
}

export function enterGuestMode() {
  sessionStorage.setItem(GUEST_KEY, '1')
  window.dispatchEvent(new CustomEvent('auth-changed', { detail: { user: getStoredUser() } }))
}

export function setAuth(token, user) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_KEY, JSON.stringify(user || null))
  window.dispatchEvent(new CustomEvent('auth-changed', { detail: { user } }))
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
  window.dispatchEvent(new CustomEvent('auth-changed', { detail: { user: null } }))
}

export function authHeaders(extra = {}) {
  const token = getAuthToken()
  return {
    ...extra,
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  }
}

export async function authFetch(url, options = {}) {
  const headers = authHeaders(options.headers || {})
  const response = await fetch(url, { ...options, headers })

  if (response.status === 401) {
    clearAuth()
  }

  return response
}

async function parseResponse(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || data.message || `请求失败：HTTP ${response.status}`)
  }
  return data
}

export async function registerUser(form) {
  const response = await fetch('/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: form.username,
      password: form.password,
      nickname: form.nickname || form.username
    })
  })

  const data = await parseResponse(response)
  setAuth(data.token, data.user)
  return data
}

export async function loginUser(form) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      username: form.username,
      password: form.password
    })
  })

  const data = await parseResponse(response)
  setAuth(data.token, data.user)
  return data
}

export async function fetchCurrentUser() {
  if (!getAuthToken()) return null

  const response = await authFetch('/api/auth/me')
  const data = await parseResponse(response)

  if (data.user) {
    localStorage.setItem(USER_KEY, JSON.stringify(data.user))
    window.dispatchEvent(new CustomEvent('auth-changed', { detail: { user: data.user } }))
  }

  return data.user || null
}

export async function loadUserRecords(params = {}) {
  const query = new URLSearchParams()

  if (params.record_type) query.set('record_type', params.record_type)
  if (params.limit) query.set('limit', params.limit)
  if (params.offset) query.set('offset', params.offset)

  const url = `/api/auth/records${query.toString() ? `?${query.toString()}` : ''}`
  const response = await authFetch(url)
  const data = await parseResponse(response)
  return data.records || []
}

export async function saveUserRecord(recordType, title, content = {}) {
  // 游客模式没有 token，直接不保存，也不报错。
  if (!getAuthToken()) return

  try {
    await authFetch('/api/auth/records', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        record_type: recordType,
        title: title || recordType,
        content
      })
    })
  } catch (error) {
    console.warn('用户记录保存失败：', error)
  }
}

export function onAuthChanged(callback) {
  const handler = event => callback(event.detail?.user || getStoredUser())
  window.addEventListener('auth-changed', handler)
  return () => window.removeEventListener('auth-changed', handler)
}
