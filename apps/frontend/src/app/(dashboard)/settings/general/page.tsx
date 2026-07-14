"use client"

import React from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { CodeBlock } from "@/components/ui/code-block"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Copy, Check } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import { toast } from "sonner"
import { useCurrentWorkspace } from "@/stores/workspace-store"
import { workspaceAPI } from "@/lib/api/endpoints/workspace"
import { useWorkspaceStore } from "@/stores/workspace-store"
import { useMutation } from "@tanstack/react-query"

export default function GeneralSettingsPage() {
  const { workspace } = useCurrentWorkspace()
  const { addWorkspace } = useWorkspaceStore()
  const workspaceId = workspace?._id ?? "your-workspace-id"
  const apiOrigin = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

  const embedCode = `<script src="${apiOrigin}/chatbot.js" data-workspace-id="${workspaceId}" async></script>`
  const wsUrl = `${apiOrigin.replace(/^http/, "ws")}/api/v1/playground/chat?workspace_id=${workspaceId}`

  const [copied, setCopied] = React.useState(false)
  const [name, setName] = React.useState(workspace?.name ?? "")

  React.useEffect(() => {
    if (workspace?.name) setName(workspace.name)
  }, [workspace?.name])

  const handleCopy = async () => {
    await navigator.clipboard.writeText(embedCode)
    setCopied(true)
    toast.success("Copied to clipboard")
    setTimeout(() => setCopied(false), 2000)
  }

  const updateMutation = useMutation({
    mutationFn: (newName: string) =>
      workspaceAPI.updateWorkspace(workspaceId, { name: newName }),
    onSuccess: (data) => {
      addWorkspace(data.data)
      toast.success("Workspace name updated")
    },
    onError: () => toast.error("Failed to update workspace name"),
  })

  const handleSaveName = (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim() || name === workspace?.name) return
    updateMutation.mutate(name.trim())
  }

  return (
    <div className="container mx-auto py-6 space-y-6 max-w-3xl">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">General Settings</h1>
        <p className="text-muted-foreground">Manage your workspace and integration settings.</p>
      </div>

      <Separator />

      <Card>
        <CardHeader>
          <CardTitle>Workspace</CardTitle>
          <CardDescription>Basic information about this workspace.</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSaveName} className="flex flex-col gap-4 sm:flex-row sm:items-end">
            <div className="flex-1 space-y-1.5">
              <Label htmlFor="ws-name">Workspace Name</Label>
              <Input
                id="ws-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My Workspace"
              />
            </div>
            <Button
              type="submit"
              disabled={updateMutation.isPending || !name.trim() || name === workspace?.name}
            >
              {updateMutation.isPending ? "Saving…" : "Save"}
            </Button>
          </form>
          <p className="mt-3 text-xs text-muted-foreground">
            Workspace ID: <code className="rounded bg-muted px-1 py-0.5">{workspaceId}</code>
          </p>
        </CardContent>
      </Card>

      <Tabs defaultValue="script" className="w-full">
        <TabsList className="grid w-full max-w-sm grid-cols-2">
          <TabsTrigger value="script">Script Tag</TabsTrigger>
          <TabsTrigger value="api">WebSocket API</TabsTrigger>
        </TabsList>

        <TabsContent value="script" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Embed Script</CardTitle>
              <CardDescription>
                Paste this single tag into the{" "}
                <code className="rounded bg-muted px-1 py-0.5 text-xs">&lt;head&gt;</code> or
                before the closing{" "}
                <code className="rounded bg-muted px-1 py-0.5 text-xs">&lt;/body&gt;</code> of
                any HTML page. The chatbot will appear automatically.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <CodeBlock code={embedCode} language="html" showLineNumbers={false} />
              <Button variant="outline" className="gap-2" onClick={handleCopy}>
                {copied ? <Check className="h-4 w-4 text-green-500" /> : <Copy className="h-4 w-4" />}
                {copied ? "Copied!" : "Copy to Clipboard"}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="api" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>WebSocket API</CardTitle>
              <CardDescription>
                Connect directly from a custom client using a WebSocket.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <Label>WebSocket endpoint</Label>
                <div className="flex gap-2">
                  <Input readOnly value={wsUrl} className="font-mono text-xs" />
                  <Button
                    variant="outline"
                    size="icon"
                    onClick={() => {
                      navigator.clipboard.writeText(wsUrl)
                      toast.success("Copied")
                    }}
                  >
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <p className="text-sm text-muted-foreground">
                Open a WebSocket connection to the endpoint above. Send plain-text messages and
                receive plain-text replies. The connection is scoped to this workspace.
              </p>
              <CodeBlock
                code={`const ws = new WebSocket("${wsUrl}");\nws.onmessage = (e) => console.log(e.data);\nws.onopen = () => ws.send("Hello!");`}
                language="javascript"
                showLineNumbers={false}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
