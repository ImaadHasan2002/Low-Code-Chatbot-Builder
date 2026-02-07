import { apiClient } from "./client";
import type { ThemeConfig } from "@/types/config";


// TODO: workspaceid cannot be undefined
export const themeAPI = {
    getTheme: (workspaceId: string | undefined): Promise<ThemeConfig> => apiClient.get(`/theme?workspace_id=${workspaceId}`).then((res) => res.data),
    createTheme: (workspaceId: string | undefined, theme: ThemeConfig): Promise<ThemeConfig> => apiClient.post(`/theme?workspace_id=${workspaceId}`, theme).then((res) => res.data),
    updateTheme: (workspaceId: string | undefined, theme: ThemeConfig): Promise<ThemeConfig> => apiClient.put(`/theme?workspace_id=${workspaceId}`, theme).then((res) => res.data),
}
