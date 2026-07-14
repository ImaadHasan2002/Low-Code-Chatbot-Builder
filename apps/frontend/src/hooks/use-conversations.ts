import { useQuery } from "@tanstack/react-query"
import { conversationsAPI } from "@/lib/api/endpoints/conversations"
import { useWorkspaceStore } from "@/stores/workspace-store"

export function useConversations(skip = 0, limit = 50) {
  const { currentWorkspaceId } = useWorkspaceStore()

  const listQuery = useQuery({
    queryKey: ["conversations", currentWorkspaceId, skip, limit],
    queryFn: () => {
      if (!currentWorkspaceId) throw new Error("No workspace selected")
      return conversationsAPI.list(currentWorkspaceId, skip, limit)
    },
    enabled: !!currentWorkspaceId,
  })

  const statsQuery = useQuery({
    queryKey: ["conversation-stats", currentWorkspaceId],
    queryFn: () => {
      if (!currentWorkspaceId) throw new Error("No workspace selected")
      return conversationsAPI.stats(currentWorkspaceId)
    },
    enabled: !!currentWorkspaceId,
    refetchInterval: 30_000,
  })

  return { listQuery, statsQuery }
}
