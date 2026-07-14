import { useMutation, useQuery } from "@tanstack/react-query"
import { toast } from "sonner"
import { workspaceAPI } from "@/lib/api/endpoints/workspace"
import { useWorkspaceStore } from "@/stores/workspace-store"

export function useWorkspace() {
  const { addWorkspace } = useWorkspaceStore()

  const createWorkspaceMutation = useMutation({
    mutationFn: workspaceAPI.createWorkspace,
    onError: (error) => {
      toast.error("Failed to create workspace", {
        description: error instanceof Error ? error.message : "Please try again",
      })
    },
    onSuccess: (data) => {
      addWorkspace(data.data)
      toast.success("Workspace created successfully")
    },
  })

  const getWorkspacesQuery = useQuery({
    queryKey: ["workspaces"],
    queryFn: async () => {
      const { data } = await workspaceAPI.getWorkspaces();
      data.forEach(addWorkspace)
      return data;
    }
  })

  return {
    createWorkspaceMutation,
    getWorkspacesQuery,
  }
} 
