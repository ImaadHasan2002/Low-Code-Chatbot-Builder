import { apiClient } from "./client";
import { WorkspaceCreate, Workspace } from "@/types/workspace";

export const workspaceAPI = {
    createWorkspace: (workspace: WorkspaceCreate) => apiClient.post<Workspace>("/workspaces", workspace),
    getWorkspaces: () => apiClient.get<Workspace[]>("/workspaces"),
    getWorkspace: (workspaceId: string) => apiClient.get<Workspace>(`/workspaces/${encodeURIComponent(workspaceId)}`),
    updateWorkspace: (workspaceId: string, data: { name: string }) =>
        apiClient.put<Workspace>(`/workspaces/${encodeURIComponent(workspaceId)}`, data),
}