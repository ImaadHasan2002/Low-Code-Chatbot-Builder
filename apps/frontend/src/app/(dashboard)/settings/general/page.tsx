"use client"

import { Button } from "@/components/ui/button"
import { CodeBlock } from "@/components/ui/code-block"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Copy, Code } from "lucide-react"
import { Separator } from "@/components/ui/separator"
import { useCurrentWorkspace } from "@/stores/workspace-store"

export default function GeneralSettingsPage() {
    const { workspace } = useCurrentWorkspace()
    const workspaceId = workspace?._id || 'your-workspace-id'

    const embedCode = `<script src="${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/chatbot.js" workspaceId-attr="${workspaceId}" strategy="lazyOnload" async/>`

    const handleCopy = () => {
        navigator.clipboard.writeText(embedCode)
    }

    return (
        <div className="container mx-auto py-6 space-y-6">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight">Integration Settings</h1>
                <p className="text-muted-foreground">Manage your chatbot integration settings</p>
            </div>
            
            <Separator />
            
            <Tabs defaultValue="script" className="w-full">
                <TabsList className="grid w-full max-w-md grid-cols-2">
                    <TabsTrigger value="script">Script Tag</TabsTrigger>
                    <TabsTrigger value="api">API</TabsTrigger>
                </TabsList>
                
                <TabsContent value="script" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>Embed Script</CardTitle>
                            <CardDescription>Copy this script tag into your website's HTML to embed the chatbot.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="mb-4">
                                <CodeBlock 
                                    code={embedCode} 
                                    language="html"
                                    showLineNumbers={false}
                                />
                            </div>
                            <Button variant="outline" className="w-full sm:w-auto gap-2" onClick={handleCopy}>
                                <Copy className="h-4 w-4" />
                                Copy to Clipboard
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>
                
                <TabsContent value="api" className="mt-4">
                    <Card>
                        <CardHeader>
                            <CardTitle>API Integration</CardTitle>
                            <CardDescription>Use our API to integrate the chatbot programmatically.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="rounded-md bg-muted p-4">
                                <p className="text-sm font-medium">API Endpoint</p>
                                <p className="mt-1 text-xs text-muted-foreground">https://api.botcraft.app/v1/chat</p>
                            </div>
                            
                            <div className="rounded-md bg-muted p-4">
                                <p className="text-sm font-medium">Authentication</p>
                                <p className="mt-1 text-xs text-muted-foreground">API Key: Use your workspace API key in the Authorization header</p>
                            </div>
                            
                            <Button variant="outline" className="gap-2">
                                <Code className="h-4 w-4" />
                                View API Docs
                            </Button>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}