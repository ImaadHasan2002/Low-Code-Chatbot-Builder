import { useShallow } from 'zustand/react/shallow'
import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'
import { immer } from 'zustand/middleware/immer'
import { devtools } from 'zustand/middleware'
import { Workspace } from '@/types/workspace'

type WorkspaceState = {
  currentWorkspaceId: string | null
  workspaces: Workspace[]
  isLoading: boolean
  error: string | null
  themeId: string | null
}

type WorkspaceActions = {
  setCurrentWorkspaceId: (id: string) => void
  clearCurrentWorkspace: () => void
  addWorkspace: (workspace: Workspace) => void
  removeWorkspace: (id: string) => void
}

const initialState: WorkspaceState = {
  currentWorkspaceId: null,
  workspaces: [],
  isLoading: false,
  error: null,
  themeId: null
}

export const useWorkspaceStore = create<WorkspaceState & WorkspaceActions>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialState,
        
        // TODO: Rename or refactor this bcz it's handling the themeId as well.
        setCurrentWorkspaceId: (id) => {
          const exists = get().workspaces.some(ws => ws._id === id)
          const themeId = get().workspaces.find((ws: Workspace) => ws._id === id)?.theme_config_id

          if (!exists) {
            console.error('Workspace not found')
            return
          }

          set({ currentWorkspaceId: id, themeId: themeId })
        },
        
        clearCurrentWorkspace: () => {
          set({ currentWorkspaceId: null })
        },
        
        addWorkspace: (workspace) => {
          if (!workspace?._id) {
            return
          }

          set((state) => {
            const existingIndex = state.workspaces.findIndex(
              (item: Workspace) => item._id === workspace._id
            )
            if (existingIndex >= 0) {
              state.workspaces[existingIndex] = workspace
            } else {
              state.workspaces.push(workspace)
            }

            const currentWorkspaceExists = state.workspaces.some(
              (item: Workspace) => item._id === state.currentWorkspaceId
            )
            if (!state.currentWorkspaceId || !currentWorkspaceExists) {
              state.currentWorkspaceId = workspace._id
              state.themeId = workspace.theme_config_id
            }
          })
        },
        
        removeWorkspace: (id) => {
          set((state) => {
            state.workspaces = state.workspaces.filter((ws: Workspace) => ws._id !== id)
            if (state.currentWorkspaceId === id) {
              state.currentWorkspaceId = null
              state.themeId = null
            }
          })
        }
      })),
      {
        name: 'workspace-store',
        storage: createJSONStorage(() => sessionStorage), // Use sessionStorage instead of localStorage
        partialize: (state) => ({ 
          currentWorkspaceId: state.currentWorkspaceId,
          themeId: state.themeId,
          workspaces: state.workspaces
        })
      }
    ),
    { name: 'WorkspaceStore' }
  )
)

export const useCurrentWorkspace = () => useWorkspaceStore(useShallow((state) => {
  return {
    workspace: state.workspaces.find((ws: Workspace) => ws._id === state.currentWorkspaceId) || null,
    themeId: state.themeId
  }
}))

export const useWorkspaces = () => useWorkspaceStore((state) => state.workspaces)
export const useWorkspaceLoading = () => useWorkspaceStore((state) => state.isLoading)
export const useWorkspaceError = () => useWorkspaceStore((state) => state.error) 
