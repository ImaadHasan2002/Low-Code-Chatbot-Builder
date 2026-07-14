import { apiClient } from "./client"

export type ConversationItem = {
  id: string
  workspace_id: string
  query: string
  response: string
  feedback?: string | null
  created_at: string
}

export type DailyCount = {
  date: string
  count: number
}

export type ConversationStats = {
  total: number
  last_7_days: DailyCount[]
  this_week: number
  last_week: number
}

export const conversationsAPI = {
  list: (workspace_id: string, skip = 0, limit = 50) =>
    apiClient.get<ConversationItem[]>(
      `/conversations/?workspace_id=${encodeURIComponent(workspace_id)}&skip=${skip}&limit=${limit}`
    ),
  stats: (workspace_id: string) =>
    apiClient.get<ConversationStats>(
      `/conversations/stats?workspace_id=${encodeURIComponent(workspace_id)}`
    ),
}
