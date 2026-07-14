import { apiClient } from "./client";
import type { CrawlJob, CrawlRequest, KnowledgeBaseItem, KnowledgeBaseType } from "@/types/knowledge-base";

export const knowledgeBaseAPI = {
  uploadFile: ({workspace_id, file}: {workspace_id: string, file: File}) => {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("workspace_id", workspace_id);
    return apiClient.post("/knowledge-base/upload", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  scrapeLink: ({workspace_id, link}: {workspace_id: string, link: string}) =>
    apiClient.post(`/knowledge-base/link?workspace_id=${encodeURIComponent(workspace_id)}`, link),
  crawlWebsite: ({ workspace_id, request }: { workspace_id: string, request: CrawlRequest }) =>
    apiClient.post<{ job: CrawlJob }>(
      `/knowledge-base/crawl?workspace_id=${encodeURIComponent(workspace_id)}`,
      request
    ),
  getCrawlJobs: (workspace_id: string) =>
    apiClient.get<{ jobs: CrawlJob[] }>(
      `/knowledge-base/crawl/jobs?workspace_id=${encodeURIComponent(workspace_id)}`
    ),
  getKnowledgeBasePDFs: (workspace_id: string) =>
    apiClient.get<KnowledgeBaseItem[]>(`/knowledge-base/pdfs?workspace_id=${encodeURIComponent(workspace_id)}`),
  getKnowledgeBaseFiles: (workspace_id: string, type?: KnowledgeBaseType) => {
    const typeQuery = type ? `&type=${encodeURIComponent(type)}` : ""
    return apiClient.get<KnowledgeBaseItem[]>(
      `/knowledge-base/files?workspace_id=${encodeURIComponent(workspace_id)}${typeQuery}`
    )
  },
  getKnowledgeBaseLinks: (workspace_id: string) =>
    apiClient.get<{ links: KnowledgeBaseItem[] }>(`/knowledge-base/links?workspace_id=${encodeURIComponent(workspace_id)}`),
  getKnowledgeBase: (knowledge_base_id: string, workspace_id: string) =>
    apiClient.get<KnowledgeBaseItem>(
      `/knowledge-base/${encodeURIComponent(knowledge_base_id)}?workspace_id=${encodeURIComponent(workspace_id)}`
    ),
  deleteKnowledgeBase: (knowledge_base_id: string, workspace_id: string) => 
    apiClient.delete(
      `/knowledge-base/${encodeURIComponent(knowledge_base_id)}?workspace_id=${encodeURIComponent(workspace_id)}`
    )
}
