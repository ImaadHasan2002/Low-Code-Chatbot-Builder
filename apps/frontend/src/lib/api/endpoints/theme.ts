import { apiClient } from "./client";
import type { ThemeConfig } from "@/types/config";

type ThemePayload = {
    theme?: string;
    position?: string;
    primary_color?: string;
    secondary_color?: string;
    text_color?: string;
    header_text?: string;
    input_placeholder?: string;
    width?: string;
    height?: string;
    border_radius?: string;
    launcher?: boolean;
    show_header?: boolean;
}

function toThemeConfig(payload: ThemePayload): ThemeConfig {
    return {
        theme: payload.theme ?? "light",
        position: payload.position ?? "bottom-right",
        primaryColor: payload.primary_color ?? "#3B82F6",
        secondaryColor: payload.secondary_color ?? "#F3F4F6",
        textColor: payload.text_color ?? "#000000",
        headerText: payload.header_text ?? "Chat with me",
        inputPlaceholder: payload.input_placeholder ?? "Type your message here...",
        width: payload.width ?? "350px",
        height: payload.height ?? "500px",
        borderRadius: payload.border_radius ?? "8px",
        launcher: payload.launcher ?? true,
        showHeader: payload.show_header ?? true,
    }
}

function toThemePayload(config: ThemeConfig): ThemePayload {
    return {
        theme: config.theme,
        position: config.position,
        primary_color: config.primaryColor,
        secondary_color: config.secondaryColor,
        text_color: config.textColor,
        header_text: config.headerText,
        input_placeholder: config.inputPlaceholder,
        width: config.width,
        height: config.height,
        border_radius: config.borderRadius,
        launcher: config.launcher,
        show_header: config.showHeader,
    }
}


// TODO: workspaceid cannot be undefined
export const themeAPI = {
    getTheme: (workspaceId: string | undefined): Promise<ThemeConfig> =>
        apiClient.get<ThemePayload>(`/theme?workspace_id=${workspaceId}`).then((res) => toThemeConfig(res.data)),
    createTheme: (workspaceId: string | undefined, theme: ThemeConfig): Promise<ThemeConfig> =>
        apiClient.post<ThemePayload>(`/theme?workspace_id=${workspaceId}`, toThemePayload(theme)).then((res) => toThemeConfig(res.data)),
    updateTheme: (workspaceId: string | undefined, theme: ThemeConfig): Promise<ThemeConfig> =>
        apiClient.put<ThemePayload>(`/theme?workspace_id=${workspaceId}`, toThemePayload(theme)).then((res) => toThemeConfig(res.data)),
}
