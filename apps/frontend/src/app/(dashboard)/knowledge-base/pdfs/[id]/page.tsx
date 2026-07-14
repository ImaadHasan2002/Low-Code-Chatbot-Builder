"use client"

import * as React from "react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import {
  ArrowLeft,
  Copy,
  ExternalLink,
  FileText,
  Loader2,
  MessageCircle,
  Trash2,
} from "lucide-react"
import { toast } from "sonner"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useKnowledgeBase } from "@/hooks/use-knowledge-base"
import { useWorkspaceStore } from "@/stores/workspace-store"

function formatDateTime(value: string) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return "Unknown"
  }

  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  })
}

export default function KnowledgeBasePDFDetailPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const id = params.id
  const { currentWorkspaceId } = useWorkspaceStore()
  const { getKnowledgeBaseQuery, deleteKnowledgeBaseMutation } =
    useKnowledgeBase(id)

  const pdf = getKnowledgeBaseQuery.data?.data

  const copySourceUrl = React.useCallback(async () => {
    if (!pdf?.file_url) return
    await navigator.clipboard.writeText(pdf.file_url)
    toast.success("Copied")
  }, [pdf?.file_url])

  const deletePdf = React.useCallback(() => {
    if (!pdf) return

    const confirmed = window.confirm(`Delete "${pdf.name}" from this workspace?`)
    if (!confirmed) return

    deleteKnowledgeBaseMutation.mutate(pdf._id, {
      onSuccess: () => router.push("/knowledge-base/pdfs"),
    })
  }, [deleteKnowledgeBaseMutation, pdf, router])

  if (!currentWorkspaceId) {
    return (
      <Alert>
        <AlertTitle>No workspace selected</AlertTitle>
        <AlertDescription>
          Select a workspace before viewing this PDF.
        </AlertDescription>
      </Alert>
    )
  }

  if (getKnowledgeBaseQuery.isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-9 w-48" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-[60vh] w-full" />
      </div>
    )
  }

  if (getKnowledgeBaseQuery.isError || !pdf) {
    return (
      <div className="space-y-4">
        <Button variant="outline" asChild>
          <Link href="/knowledge-base/pdfs">
            <ArrowLeft />
            Back
          </Link>
        </Button>
        <Alert variant="destructive">
          <AlertTitle>PDF not found</AlertTitle>
          <AlertDescription>
            This knowledge source may have been deleted or belongs to another workspace.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Button variant="outline" asChild>
          <Link href="/knowledge-base/pdfs">
            <ArrowLeft />
            Back
          </Link>
        </Button>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="outline" onClick={copySourceUrl}>
            <Copy />
            Copy URL
          </Button>
          <Button variant="outline" asChild>
            <a href={pdf.file_url} target="_blank" rel="noreferrer">
              <ExternalLink />
              Open PDF
            </a>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/knowledge-base/chat">
              <MessageCircle />
              Chat
            </Link>
          </Button>
          <Button
            variant="destructive"
            onClick={deletePdf}
            disabled={deleteKnowledgeBaseMutation.isPending}
          >
            {deleteKnowledgeBaseMutation.isPending ? (
              <Loader2 className="animate-spin" />
            ) : (
              <Trash2 />
            )}
            Delete
          </Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div className="min-w-0 space-y-2">
              <CardTitle className="flex min-w-0 items-center gap-2 text-xl">
                <FileText className="h-5 w-5 shrink-0 text-muted-foreground" />
                <span className="truncate">{pdf.name}</span>
              </CardTitle>
              <CardDescription className="break-all">{pdf.file_url}</CardDescription>
            </div>
            <Badge variant="secondary">PDF</Badge>
          </div>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 text-sm sm:grid-cols-3">
            <div>
              <dt className="text-muted-foreground">Created</dt>
              <dd className="font-medium">{formatDateTime(pdf.created_at)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Last Modified</dt>
              <dd className="font-medium">{formatDateTime(pdf.updated_at)}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Document ID</dt>
              <dd className="break-all font-mono text-xs">{pdf._id}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>

      <div className="overflow-hidden rounded-md border bg-background">
        <iframe
          src={pdf.file_url}
          title={pdf.name}
          className="h-[70vh] w-full"
        />
      </div>
    </div>
  )
}
