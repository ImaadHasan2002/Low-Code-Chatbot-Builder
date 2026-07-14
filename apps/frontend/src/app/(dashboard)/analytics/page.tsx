"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts"
import { MessageSquare, TrendingUp, TrendingDown, Minus } from "lucide-react"
import { useConversations } from "@/hooks/use-conversations"
import { useWorkspaceStore } from "@/stores/workspace-store"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

function StatCard({
  title,
  value,
  sub,
  loading,
}: {
  title: string
  value: React.ReactNode
  sub?: React.ReactNode
  loading?: boolean
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <>
            <Skeleton className="h-8 w-24 mb-1" />
            <Skeleton className="h-3 w-32" />
          </>
        ) : (
          <>
            <div className="text-2xl font-bold">{value}</div>
            {sub && <p className="text-xs text-muted-foreground mt-1">{sub}</p>}
          </>
        )}
      </CardContent>
    </Card>
  )
}

function WeekTrend({ thisWeek, lastWeek }: { thisWeek: number; lastWeek: number }) {
  if (lastWeek === 0 && thisWeek === 0) return <span className="text-muted-foreground">—</span>
  if (lastWeek === 0) return <span className="text-green-600 flex items-center gap-1"><TrendingUp className="h-3 w-3" /> New this week</span>
  const pct = Math.round(((thisWeek - lastWeek) / lastWeek) * 100)
  if (pct > 0) return <span className="text-green-600 flex items-center gap-1"><TrendingUp className="h-3 w-3" /> +{pct}% vs last week</span>
  if (pct < 0) return <span className="text-red-500 flex items-center gap-1"><TrendingDown className="h-3 w-3" /> {pct}% vs last week</span>
  return <span className="text-muted-foreground flex items-center gap-1"><Minus className="h-3 w-3" /> Same as last week</span>
}

export default function AnalyticsPage() {
  const { currentWorkspaceId } = useWorkspaceStore()
  const { listQuery, statsQuery } = useConversations(0, 10)

  const stats = statsQuery.data?.data
  const conversations = listQuery.data?.data ?? []
  const loading = statsQuery.isLoading

  if (!currentWorkspaceId) {
    return (
      <div className="container mx-auto p-6">
        <Alert>
          <AlertTitle>No workspace selected</AlertTitle>
          <AlertDescription>Select or create a workspace to view analytics.</AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          title="Total Conversations"
          value={stats?.total ?? 0}
          sub={
            stats ? (
              <WeekTrend thisWeek={stats.this_week} lastWeek={stats.last_week} />
            ) : null
          }
          loading={loading}
        />
        <StatCard
          title="This Week"
          value={stats?.this_week ?? 0}
          sub="Conversations in the last 7 days"
          loading={loading}
        />
        <StatCard
          title="Last Week"
          value={stats?.last_week ?? 0}
          sub="Conversations 8–14 days ago"
          loading={loading}
        />
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Daily Conversations</CardTitle>
            <CardDescription>Messages handled per day over the last 7 days</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-[280px] w-full" />
            ) : (
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stats?.last_7_days ?? []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(v: string) =>
                        new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric" })
                      }
                      tick={{ fontSize: 11 }}
                    />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip
                      labelFormatter={(v: string) =>
                        new Date(v).toLocaleDateString("en-US", {
                          weekday: "short",
                          month: "short",
                          day: "numeric",
                        })
                      }
                    />
                    <Bar dataKey="count" fill="#3B82F6" name="Conversations" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Conversation Trend</CardTitle>
            <CardDescription>Cumulative conversations over the last 7 days</CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <Skeleton className="h-[280px] w-full" />
            ) : (
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={(stats?.last_7_days ?? []).reduce<{ date: string; cumulative: number }[]>(
                      (acc, d) => {
                        const prev = acc[acc.length - 1]?.cumulative ?? 0
                        return [...acc, { date: d.date, cumulative: prev + d.count }]
                      },
                      []
                    )}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(v: string) =>
                        new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric" })
                      }
                      tick={{ fontSize: 11 }}
                    />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip
                      labelFormatter={(v: string) =>
                        new Date(v).toLocaleDateString("en-US", {
                          weekday: "short",
                          month: "short",
                          day: "numeric",
                        })
                      }
                    />
                    <Line
                      type="monotone"
                      dataKey="cumulative"
                      stroke="#8B5CF6"
                      name="Cumulative"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            Recent Conversations
          </CardTitle>
          <CardDescription>Last 10 messages sent to your chatbot</CardDescription>
        </CardHeader>
        <CardContent>
          {listQuery.isLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 4 }).map((_, i) => (
                <Skeleton key={i} className="h-16 w-full" />
              ))}
            </div>
          ) : conversations.length === 0 ? (
            <p className="text-sm text-muted-foreground py-8 text-center">
              No conversations yet. Embed the chatbot on your site to start collecting data.
            </p>
          ) : (
            <div className="space-y-3">
              {conversations.map((conv) => (
                <div key={conv.id} className="rounded-lg border p-3 space-y-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium truncate">{conv.query}</p>
                    <span className="text-xs text-muted-foreground shrink-0">
                      {new Date(conv.created_at).toLocaleDateString("en-US", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground line-clamp-2">{conv.response}</p>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
