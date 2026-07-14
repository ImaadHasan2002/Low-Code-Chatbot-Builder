import { apiClient } from './client'

export const chatbotAPI = {
    query: ({ workspace_id, query }: { workspace_id: string; query: string }) =>
        apiClient.post<{ response: string }>(
            `/chatbot/query?workspace_id=${encodeURIComponent(
                workspace_id
            )}&query=${encodeURIComponent(query)}`
        ),
    feedback: ({
        conversation_id,
        feedback,
    }: {
        conversation_id: string
        feedback: string
    }) =>
        apiClient.post<{ message: string }>(
            `/chatbot/feedback?conversation_id=${encodeURIComponent(
                conversation_id
            )}&feedback=${encodeURIComponent(feedback)}`
        ),
}
