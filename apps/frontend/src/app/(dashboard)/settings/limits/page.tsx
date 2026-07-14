"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Skeleton } from "@/components/ui/skeleton"
import { useConversations } from "@/hooks/use-conversations"
import { useKnowledgeBase } from "@/hooks/use-knowledge-base"
import { useWorkspaceStore } from "@/stores/workspace-store"

const CRAWL_PAGE_LIMIT = 500
const CONVERSATION_LIMIT = 10_000
const FILE_LIMIT = 200

function LimitRow({
  label,
  value,
  limit,
  unit,
  loading,
}: {
  label: string
  value: number
  limit: number
  unit: string
  loading?: boolean
}) {
  const pct = Math.min(100, Math.round((value / limit) * 100))
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="font-medium">{label}</span>
        {loading ? (
          <Skeleton className="h-4 w-24" />
        ) : (
          <span className="text-muted-foreground">
            {value.toLocaleString()} / {limit.toLocaleString()} {unit}
          </span>
        )}
      </div>
      {loading ? <Skeleton className="h-2 w-full" /> : <Progress value={pct} className="h-2" />}
    </div>
  )
}

export default function SettingsLimitsPage() {
  const { currentWorkspaceId } = useWorkspaceStore()
  const { statsQuery } = useConversations()
  const { getPDFsQuery, getLinksQuery, getFilesQuery } = useKnowledgeBase(undefined, "all")

  const totalConversations = statsQuery.data?.data?.total ?? 0
  const totalPages = getLinksQuery.data?.data?.links?.length ?? 0
  const totalFiles =
    (getPDFsQuery.data?.data?.length ?? 0) + (getFilesQuery.data?.data?.length ?? 0)

  const loading = !currentWorkspaceId || statsQuery.isLoading || getPDFsQuery.isLoading

  return (
    <div className="container mx-auto py-6 max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Usage Limits</h1>
        <p className="text-muted-foreground mt-1">
          Current resource usage for this workspace.
        </p>
      </div>

      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>Self-hosted Limits</CardTitle>
          <CardDescription>
            These soft limits reflect sensible defaults. Adjust them in your environment variables
            or Advanced Settings.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <LimitRow
            label="Conversations"
            value={totalConversations}
            limit={CONVERSATION_LIMIT}
            unit="messages"
            loading={loading}
          />
          <LimitRow
            label="Crawled Pages"
            value={totalPages}
            limit={CRAWL_PAGE_LIMIT}
            unit="pages"
            loading={loading}
          />
          <LimitRow
            label="Uploaded Files"
            value={totalFiles}
            limit={FILE_LIMIT}
            unit="files"
            loading={loading}
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>API Rate Limits</CardTitle>
          <CardDescription>Limits enforced by your LLM provider (OpenAI).</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2 text-sm text-muted-foreground">
          <p>Rate limits depend on your OpenAI tier. BotCraft does not add additional throttling.</p>
          <p>
            Configure your OpenAI API key in{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">.env</code> under{" "}
            <code className="rounded bg-muted px-1 py-0.5 text-xs">OPENAI_API_KEY</code>.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
