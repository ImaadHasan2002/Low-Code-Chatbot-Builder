"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { CheckCircle2 } from "lucide-react"

const PLAN_FEATURES = [
  "Unlimited workspaces",
  "Recursive website crawling (up to 500 pages per crawl)",
  "PDF, CSV, XLS, image, and video uploads",
  "Custom theme and branding",
  "WebSocket-powered embedded chatbot",
  "RAG with Pinecone vector search",
  "Conversation history and analytics",
  "Background crawl jobs with status tracking",
]

export default function SettingsBillingPage() {
  return (
    <div className="container mx-auto py-6 max-w-2xl space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Billing</h1>
        <p className="text-muted-foreground mt-1">Manage your subscription and usage.</p>
      </div>

      <Separator />

      <Card>
        <CardHeader className="flex flex-row items-start justify-between gap-4">
          <div>
            <CardTitle>Current Plan</CardTitle>
            <CardDescription>You are on the open-source self-hosted edition.</CardDescription>
          </div>
          <Badge variant="secondary" className="shrink-0">Free / Self-hosted</Badge>
        </CardHeader>
        <CardContent className="space-y-4">
          <ul className="grid gap-2">
            {PLAN_FEATURES.map((f) => (
              <li key={f} className="flex items-center gap-2 text-sm">
                <CheckCircle2 className="h-4 w-4 text-green-500 shrink-0" />
                {f}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Cloud Hosting</CardTitle>
          <CardDescription>
            Want a managed, always-on deployment without running your own servers?
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Cloud plans include automatic scaling, managed MongoDB and Pinecone, SSL, and
            one-click deploys. Pricing is based on monthly active conversations.
          </p>
          <Button variant="outline" disabled>
            Coming soon
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
