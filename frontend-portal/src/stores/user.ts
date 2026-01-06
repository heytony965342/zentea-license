import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authApi } from '@/api'

interface User {
  id: number
  username: string
  email: string
  role: string
  company_name?: string
  contact_name?: string
  phone?: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('portal_token'))

  const login = async (username: string, password: string) => {
    const res = await authApi.login(username, password)
    if (res.code === 200) {
      token.value = res.data.access_token
      user.value = res.data.user
      localStorage.setItem('portal_token', res.data.access_token)
      return true
    }
    return false
  }

  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('portal_token')
  }

  const fetchUser = async () => {
    if (!token.value) return
    try {
      const res = await authApi.getMe()
      if (res.code === 200) {
        user.value = res.data
      }
    } catch {
      logout()
    }
  }

  return { user, token, login, logout, fetchUser }
})

