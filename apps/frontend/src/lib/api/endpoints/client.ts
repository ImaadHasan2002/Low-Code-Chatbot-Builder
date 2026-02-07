// lib/api/client.ts
import axios from 'axios'

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true
})

// Add interceptors for auth tokens
// apiClient.interceptors.request.use(config => {
//   const token = document.cookie.split('; ').find(row => row.startsWith('access_token='))?.split('=')[1]
//   if (token) config.headers.Authorization = `Bearer ${token}`
//   return config
// })