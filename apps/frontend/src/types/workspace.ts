

export type Workspace = {
  name: string
  _id: string
  owner_id: string
  members: string[]
  created_at: Date
  updated_at: Date
  theme_config_id: string
  advanced_config_id: string
}

export type WorkspaceCreate = {
  name: string
}
