import { useMutation, useQuery } from "@tanstack/react-query"
import { knowledgeBaseAPI } from "@/lib/api/endpoints/knowledge-base"
import { useWorkspaceStore } from "@/stores/workspace-store"
import { useMemo } from "react"

export function useKnowledgeBase() {
  const { currentWorkspaceId } = useWorkspaceStore()
  
  const uploadFileMutation = useMutation({
    mutationFn: (file: File) => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.uploadFile({ workspace_id: currentWorkspaceId, file })
    }
  })

  const scrapeLinkMutation = useMutation({
    mutationFn: (link: string) => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.scrapeLink({ workspace_id: currentWorkspaceId, link })
    }
  })
  const getPDFsQuery = useQuery({
    queryKey: ["knowledge-base-pdfs", currentWorkspaceId],
    queryFn: () => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.getKnowledgeBasePDFs(currentWorkspaceId)
    },
    enabled: !!currentWorkspaceId
  })

  const getLinksQuery = useQuery({
    queryKey: ["knowledge-base-links", currentWorkspaceId],
    queryFn: () => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.getKnowledgeBaseLinks(currentWorkspaceId)
    },
    enabled: !!currentWorkspaceId
  })

  return useMemo(() => ({
    uploadFileMutation,
    getPDFsQuery,
    getLinksQuery,
    scrapeLinkMutation
  }), [uploadFileMutation, getPDFsQuery, getLinksQuery, scrapeLinkMutation])
}
