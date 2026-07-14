export type KnowledgeBaseType =
  | "pdf"
  | "csv"
  | "link"
  | "video"
  | "text"
  | "image"
  | "audio"
  | "xlsx"

export type KnowledgeBaseItem = {
  _id: string
  workspace_id: string
  type: KnowledgeBaseType
  file_url: string
  created_at: string
  updated_at: string
  name: string
  status?: "pending" | "indexed" | "failed"
  metadata?: Record<string, unknown>
}

export type CrawlRequest = {
  base_url: string
  max_pages: number
  max_depth: number
  include_paths: string[]
  exclude_paths: string[]
}

export type CrawlJob = {
  job_id: string
  workspace_id: string
  job_type: string
  status: "pending" | "running" | "completed" | "failed"
  message?: string | null
  processed_items: number
  total_items: number
  payload: Partial<CrawlRequest>
  created_at: string
  updated_at: string
  completed_at?: string | null
}
