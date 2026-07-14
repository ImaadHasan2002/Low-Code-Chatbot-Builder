// lib/api/client.ts
import axios from 'axios'

// All backend routes are mounted under /api/v1 — the base URL must include it.
// NEXT_PUBLIC_API_URL should be the backend origin, e.g. http://localhost:8000
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: true // send/receive auth cookies
})
