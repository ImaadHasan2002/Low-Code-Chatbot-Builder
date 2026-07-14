"use client"

import * as React from "react"
import { Copy, ExternalLink, Loader2, Trash2, Upload } from "lucide-react"
import { toast } from "sonner"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useKnowledgeBase } from "@/hooks/use-knowledge-base"
import { useWorkspaceStore } from "@/stores/workspace-store"
import type { KnowledgeBaseItem, KnowledgeBaseType } from "@/types/knowledge-base"

type FileUploadPageProps = {
  title: string
  description: string
  accept: string
  uploadLabel: string
  visibleTypes: KnowledgeBaseType[]
  emptyLabel: string
}

function formatDate(value: string) {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return "Unknown"
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  })
}

export function FileUploadPage({
  title,
  description,
  accept,
  uploadLabel,
  visibleTypes,
  emptyLabel,
}: FileUploadPageProps) {
  const { currentWorkspaceId } = useWorkspaceStore()
  const {
    uploadFileMutation,
    deleteKnowledgeBaseMutation,
    getFilesQuery,
  } = useKnowledgeBase(undefined, "all")
  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const [filter, setFilter] = React.useState("")

  const rows = React.useMemo(() => {
    const items = getFilesQuery.data?.data ?? []
    return items
      .filter((item) => visibleTypes.includes(item.type))
      .filter((item) => item.name.toLowerCase().includes(filter.toLowerCase()))
  }, [filter, getFilesQuery.data?.data, visibleTypes])

  const handleUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return
    uploadFileMutation.mutate(file, {
      onSettled: () => {
        event.target.value = ""
      },
    })
  }

  const copyUrl = async (item: KnowledgeBaseItem) => {
    await navigator.clipboard.writeText(item.file_url)
    toast.success("Copied")
  }

  const deleteItem = (item: KnowledgeBaseItem) => {
    if (!window.confirm(`Delete "${item.name}" from this workspace?`)) return
    deleteKnowledgeBaseMutation.mutate(item._id)
  }

  if (!currentWorkspaceId) {
    return (
      <Alert>
        <AlertTitle>No workspace selected</AlertTitle>
        <AlertDescription>
          Create or select a workspace before adding knowledge sources.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="space-y-1">
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadFileMutation.isPending}
          >
            {uploadFileMutation.isPending ? (
              <Loader2 className="animate-spin" />
            ) : (
              <Upload />
            )}
            {uploadLabel}
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept={accept}
            className="hidden"
            onChange={handleUpload}
          />
        </div>
      </div>

      <Input
        placeholder="Filter files..."
        value={filter}
        onChange={(event) => setFilter(event.target.value)}
        className="max-w-sm"
      />

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Name</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Added</TableHead>
              <TableHead className="w-[140px] text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {getFilesQuery.isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
                  Loading files...
                </TableCell>
              </TableRow>
            ) : rows.length ? (
              rows.map((item) => (
                <TableRow key={item._id}>
                  <TableCell className="max-w-xl truncate font-medium">
                    {item.name}
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">{item.type.toUpperCase()}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={item.status === "failed" ? "destructive" : "secondary"}>
                      {item.status ?? "indexed"}
                    </Badge>
                  </TableCell>
                  <TableCell>{formatDate(item.created_at)}</TableCell>
                  <TableCell>
                    <div className="flex justify-end gap-1">
                      <Button variant="ghost" size="icon" asChild>
                        <a href={item.file_url} target="_blank" rel="noreferrer" aria-label="Open file">
                          <ExternalLink />
                        </a>
                      </Button>
                      <Button variant="ghost" size="icon" onClick={() => copyUrl(item)}>
                        <Copy />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        disabled={
                          deleteKnowledgeBaseMutation.isPending &&
                          deleteKnowledgeBaseMutation.variables === item._id
                        }
                        onClick={() => deleteItem(item)}
                      >
                        {deleteKnowledgeBaseMutation.isPending &&
                        deleteKnowledgeBaseMutation.variables === item._id ? (
                          <Loader2 className="animate-spin" />
                        ) : (
                          <Trash2 />
                        )}
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center">
                  {emptyLabel}
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
