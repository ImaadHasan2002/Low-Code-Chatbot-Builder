import { useMutation, useQuery } from "@tanstack/react-query";
import { themeAPI } from "@/lib/api/endpoints/theme";
import { ThemeConfig } from "@/types/config";
import { useCurrentWorkspace } from "@/stores/workspace-store";

export function useTheme() {
    const { workspace } = useCurrentWorkspace();
    const workspaceId = workspace?._id;


    const getThemeQuery = useQuery({
        queryKey: ["theme_config_id", workspaceId],
        queryFn: () => themeAPI.getTheme(workspaceId)
    })

    const updateThemeMutation = useMutation({
        mutationFn: (theme: ThemeConfig) => themeAPI.updateTheme(workspaceId, theme)
    })

    return {
        getThemeQuery,
        updateThemeMutation
    }
}