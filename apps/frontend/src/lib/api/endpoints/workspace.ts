import { apiClient } from "./client";
import { WorkspaceCreate, Workspace } from "@/types/workspace";

export const workspaceAPI = {
    createWorkspace: (workspace: WorkspaceCreate) => apiClient.post("/workspaces", workspace),
    getWorkspaces: () => apiClient.get<Workspace[]>("/workspaces"),
    // getWorkspace: (workspaceId: string) => apiClient.get(`/workspaces/${workspaceId}`),    
}