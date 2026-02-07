// in botcraft-frontend/src/hooks/use-advanced-config.ts
import { useQuery, useMutation, QueryClient } from "@tanstack/react-query";
import { advancedConfigAPI } from "@/lib/api/endpoints/advanced-config";
import type { AdvancedConfig } from "@/types/config";
import { useCurrentWorkspace } from "@/stores/workspace-store";

export function useAdvancedConfig() {
    const { workspace } = useCurrentWorkspace();
    const workspaceId = workspace?._id;

    console.log("Workspace ID in useAdvancedConfig: ", workspaceId);

    const getAdvancedConfigQuery = useQuery({
        queryKey: ["advanced-config", workspaceId],
        queryFn: () => workspaceId ? advancedConfigAPI.getAdvancedConfig(workspaceId) : null,
        enabled: !!workspaceId,
    });

    const updateAdvancedConfigMutation = useMutation({
        mutationFn: (advancedConfig: AdvancedConfig) => 
            workspaceId ? advancedConfigAPI.updateAdvancedConfig(workspaceId, advancedConfig) : Promise.reject("No workspace ID"),
    });

    return {
        getAdvancedConfigQuery,
        updateAdvancedConfigMutation
    };
}