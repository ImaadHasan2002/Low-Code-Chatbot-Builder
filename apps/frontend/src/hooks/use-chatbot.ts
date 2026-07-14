import { useMutation } from '@tanstack/react-query'
import { useMemo } from 'react'
import { chatbotAPI } from '@/lib/api/endpoints/chatbot'
import { useWorkspaceStore } from '@/stores/workspace-store'

export function useChatbot() {
    const { currentWorkspaceId } = useWorkspaceStore()

    const queryMutation = useMutation({
        mutationFn: (query: string) => {
            if (!currentWorkspaceId) {
                throw new Error('No workspace selected')
            }
            return chatbotAPI.query({ workspace_id: currentWorkspaceId, query })
        },
    })

    return useMemo(
        () => ({
            currentWorkspaceId,
            queryMutation,
        }),
        [currentWorkspaceId, queryMutation]
    )
}
