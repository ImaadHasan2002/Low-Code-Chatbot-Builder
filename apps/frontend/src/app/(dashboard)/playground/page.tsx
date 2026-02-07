"use client"

import { useState } from "react"
import { Send } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { useWebSocket } from "@/hooks/use-websocket"
import { useCurrentWorkspace } from "@/stores/workspace-store"


export default function Playground() {
  const [input, setInput] = useState("")
  const { workspace } = useCurrentWorkspace()
  const { conversation, sendMessage } = useWebSocket({path: "playground/chat", workspaceId: workspace?._id});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return
    
    sendMessage(input);

    setInput("");
  }

  return (
    <div className="h-full flex flex-col">
      <Card className="flex-1 flex flex-col">
        <CardHeader>
          <h1 className="text-xl font-semibold">Playground</h1>
        </CardHeader>
        <Separator />
        <CardContent className="flex-1 flex flex-col p-0">
          <ScrollArea className="flex-1 p-4 min-h-[calc(100vh-270px)] max-h-[calc(100vh-270px)]">
            <div className="space-y-4">
              {conversation?.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.isUser ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg p-3 ${
                      message.isUser
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm">{message.text}</p>
                    <p className="text-xs mt-1 opacity-80">
                      {message.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </ScrollArea>
          <form onSubmit={handleSubmit} className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1"
              />
              <Button type="submit" size="icon">
                <Send className="h-4 w-4" />
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}