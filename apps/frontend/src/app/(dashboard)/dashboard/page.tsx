"use client"

import Link from "next/link"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { MessageSquare, Globe, FileText, BarChart2, Settings, ArrowRight } from "lucide-react"
import { useConversations } from "@/hooks/use-conversations"
import { useKnowledgeBase } from "@/hooks/use-knowledge-base"
import { useWorkspaceStore } from "@/stores/workspace-store"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

function QuickCard({
  title,
  value,
  icon: Icon,
  description,
  href,
  loading,
}: {
  title: string
  value: React.ReactNode
  icon: React.ElementType
  description: string
  href: string
  loading?: boolean
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-20" />
        ) : (
          <div className="text-2xl font-bold">{value}</div>
        )}
        <p className="text-xs text-muted-foreground mt-1">{description}</p>
        <Link href={href}>
          <Button variant="link" className="px-0 h-auto text-xs mt-2">
            View <ArrowRight className="ml-1 h-3 w-3" />
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  const { currentWorkspaceId } = useWorkspaceStore()
  const { statsQuery, listQuery } = useConversations(0, 5)
  const { getPDFsQuery, getLinksQuery, getCrawlJobsQuery } = useKnowledgeBase(undefined, undefined)

  const stats = statsQuery.data?.data
  const recentConversations = listQuery.data?.data ?? []
  const pdfs = getPDFsQuery.data?.data ?? []
  const links = getLinksQuery.data?.data?.links ?? []
  const crawlJobs = getCrawlJobsQuery.data?.data?.jobs ?? []
  const activeCrawl = crawlJobs.find((j) => j.status === "running" || j.status === "pending")

  if (!currentWorkspaceId) {
    return (
      <div className="container mx-auto p-6">
        <Alert>
          <AlertTitle>No workspace selected</AlertTitle>
          <AlertDescription>
            <Link href="/onboarding">
              <Button variant="link" className="px-0">Create your first workspace</Button>
            </Link>{" "}
            to get started.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        {activeCrawl && (
          <Badge variant="secondary" className="animate-pulse">
            Crawling website…
          </Badge>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <QuickCard
          title="Total Conversations"
          value={stats?.total ?? 0}
          icon={MessageSquare}
          description="All-time chatbot messages"
          href="/analytics"
          loading={statsQuery.isLoading}
        />
        <QuickCard
          title="Pages Indexed"
          value={links.length}
          icon={Globe}
          description="Crawled website pages"
          href="/knowledge-base/links"
          loading={getLinksQuery.isLoading}
        />
        <QuickCard
          title="Documents"
          value={pdfs.length}
          icon={FileText}
          description="Uploaded PDFs and files"
          href="/knowledge-base/pdfs"
          loading={getPDFsQuery.isLoading}
        />
        <QuickCard
          title="This Week"
          value={stats?.this_week ?? 0}
          icon={BarChart2}
          description="Conversations last 7 days"
          href="/analytics"
          loading={statsQuery.isLoading}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Recent Conversations
            </CardTitle>
            <CardDescription>Last 5 chatbot interactions</CardDescription>
          </CardHeader>
          <CardContent>
            {listQuery.isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 3 }).map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : recentConversations.length === 0 ? (
              <div className="py-8 text-center space-y-3">
                <p className="text-sm text-muted-foreground">No conversations yet.</p>
                <Link href="/settings/general">
                  <Button variant="outline" size="sm">
                    Get embed code
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {recentConversations.map((conv) => (
                  <div key={conv.id} className="flex flex-col gap-0.5 rounded-md border px-3 py-2">
                    <p className="text-sm font-medium truncate">{conv.query}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(conv.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                ))}
                <Link href="/analytics">
                  <Button variant="ghost" size="sm" className="w-full mt-1">
                    View all <ArrowRight className="ml-1 h-3 w-3" />
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Quick Actions
            </CardTitle>
            <CardDescription>Common tasks for your workspace</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-2">
            <Link href="/knowledge-base/links">
              <Button variant="outline" className="w-full justify-start">
                <Globe className="mr-2 h-4 w-4" />
                Crawl a website
              </Button>
            </Link>
            <Link href="/knowledge-base/pdfs">
              <Button variant="outline" className="w-full justify-start">
                <FileText className="mr-2 h-4 w-4" />
                Upload documents
              </Button>
            </Link>
            <Link href="/settings/theme">
              <Button variant="outline" className="w-full justify-start">
                <Settings className="mr-2 h-4 w-4" />
                Customize appearance
              </Button>
            </Link>
            <Link href="/settings/general">
              <Button variant="outline" className="w-full justify-start">
                <MessageSquare className="mr-2 h-4 w-4" />
                Get embed code
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
