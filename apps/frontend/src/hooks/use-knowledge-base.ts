import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { knowledgeBaseAPI } from "@/lib/api/endpoints/knowledge-base"
import { useWorkspaceStore } from "@/stores/workspace-store"
import { useMemo } from "react"
import { toast } from "sonner"
import type { CrawlRequest, KnowledgeBaseType } from "@/types/knowledge-base"

function getErrorMessage(error: unknown) {
  if (
    typeof error === "object" &&
    error !== null &&
    "response" in error
  ) {
    const apiError = error as { response?: { data?: { detail?: string } } }
    return apiError.response?.data?.detail
  }

  return error instanceof Error ? error.message : "Please try again"
}

export function useKnowledgeBase(knowledgeBaseId?: string, fileType?: KnowledgeBaseType | "all") {
  const { currentWorkspaceId } = useWorkspaceStore()
  const queryClient = useQueryClient()
  
  const uploadFileMutation = useMutation({
    mutationFn: (file: File) => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.uploadFile({ workspace_id: currentWorkspaceId, file })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-base-pdfs", currentWorkspaceId] })
      queryClient.invalidateQueries({ queryKey: ["knowledge-base-files", currentWorkspaceId] })
      toast.success("File uploaded and indexed")
    },
    onError: (error) => {
      toast.error("File upload failed", {
        description: getErrorMessage(error),
      })
    }
  })

  const crawlWebsiteMutation = useMutation({
    mutationFn: (request: CrawlRequest) => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.crawlWebsite({ workspace_id: currentWorkspaceId, request })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-base-links", currentWorkspaceId] })
      queryClient.invalidateQueries({ queryKey: ["crawl-jobs", currentWorkspaceId] })
      toast.success("Crawl started")
    },
    onError: (error) => {
      toast.error("Crawl failed to start", {
        description: getErrorMessage(error),
      })
    }
  })

  const scrapeLinkMutation = useMutation({
    mutationFn: (link: string) => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.scrapeLink({ workspace_id: currentWorkspaceId, link })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-base-links", currentWorkspaceId] })
      queryClient.invalidateQueries({ queryKey: ["crawl-jobs", currentWorkspaceId] })
      toast.success("Link added and indexed")
    },
    onError: (error) => {
      toast.error("Link upload failed", {
        description: getErrorMessage(error),
      })
    }
  })

  const deleteKnowledgeBaseMutation = useMutation({
    mutationFn: (knowledgeBaseIdToDelete: string) => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.deleteKnowledgeBase(knowledgeBaseIdToDelete, currentWorkspaceId)
    },
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: ["knowledge-base-pdfs", currentWorkspaceId] })
      queryClient.invalidateQueries({ queryKey: ["knowledge-base-links", currentWorkspaceId] })
      queryClient.invalidateQueries({ queryKey: ["knowledge-base-files", currentWorkspaceId] })
      queryClient.removeQueries({ queryKey: ["knowledge-base", currentWorkspaceId, deletedId] })
      toast.success("Knowledge source deleted")
    },
    onError: (error) => {
      toast.error("Delete failed", {
        description: getErrorMessage(error),
      })
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

  const getFilesQuery = useQuery({
    queryKey: ["knowledge-base-files", currentWorkspaceId, fileType],
    queryFn: () => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.getKnowledgeBaseFiles(
        currentWorkspaceId,
        fileType === "all" ? undefined : fileType
      )
    },
    enabled: !!currentWorkspaceId && !!fileType
  })

  const getKnowledgeBaseQuery = useQuery({
    queryKey: ["knowledge-base", currentWorkspaceId, knowledgeBaseId],
    queryFn: () => {
      if (!currentWorkspaceId || !knowledgeBaseId) {
        throw new Error("No knowledge base selected")
      }
      return knowledgeBaseAPI.getKnowledgeBase(knowledgeBaseId, currentWorkspaceId)
    },
    enabled: !!currentWorkspaceId && !!knowledgeBaseId
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

  const getCrawlJobsQuery = useQuery({
    queryKey: ["crawl-jobs", currentWorkspaceId],
    queryFn: () => {
      if (!currentWorkspaceId) {
        throw new Error("No workspace selected")
      }
      return knowledgeBaseAPI.getCrawlJobs(currentWorkspaceId)
    },
    enabled: !!currentWorkspaceId,
    refetchInterval: 4000,
  })

  return useMemo(() => ({
    uploadFileMutation,
    crawlWebsiteMutation,
    deleteKnowledgeBaseMutation,
    getKnowledgeBaseQuery,
    getPDFsQuery,
    getFilesQuery,
    getLinksQuery,
    getCrawlJobsQuery,
    scrapeLinkMutation
  }), [
    uploadFileMutation,
    crawlWebsiteMutation,
    deleteKnowledgeBaseMutation,
    getKnowledgeBaseQuery,
    getPDFsQuery,
    getFilesQuery,
    getLinksQuery,
    getCrawlJobsQuery,
    scrapeLinkMutation
  ])
}
