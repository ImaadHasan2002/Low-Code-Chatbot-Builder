import { apiClient } from "./client";
import type { AdvancedConfig } from "@/types/config";

export const advancedConfigAPI = {
    getAdvancedConfig: (workspaceId: string) => apiClient.get(`/advanced-config?workspace_id=${workspaceId}`).then((res) => res.data?.advanced_config),
    createAdvancedConfig: async (workspaceId: string, advancedConfig: AdvancedConfig) =>{
        console.log("Advanced config in createAdvancedConfig: ", advancedConfig)
        return apiClient.post(`/advanced-config?workspace_id=${workspaceId}`, {advanced_config: advancedConfig}).then((res) => res.data)},
    updateAdvancedConfig: (workspaceId: string, advancedConfig: AdvancedConfig) => apiClient.put(`/advanced-config?workspace_id=${workspaceId}`, {advanced_config: advancedConfig}).then((res) => res.data),
}
