'use client'

import * as React from 'react'
import { Bot, Loader2, Send, User } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { useChatbot } from '@/hooks/use-chatbot'

type ChatMessage = {
    id: string
    text: string
    isUser: boolean
    timestamp: Date
}

export default function KnowledgeBaseChatPage() {
    const { currentWorkspaceId, queryMutation } = useChatbot()
    const [input, setInput] = React.useState('')
    const [messages, setMessages] = React.useState<ChatMessage[]>([])
    const scrollAnchorRef = React.useRef<HTMLDivElement | null>(null)

    const isSending = queryMutation.isPending
    const canSend = !!currentWorkspaceId && !!input.trim() && !isSending

    React.useEffect(() => {
        scrollAnchorRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, isSending])

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault()
        const text = input.trim()
        if (!text || !currentWorkspaceId || isSending) return

        const userMessage: ChatMessage = {
            id: crypto.randomUUID(),
            text,
            isUser: true,
            timestamp: new Date(),
        }
        setMessages((prev) => [...prev, userMessage])
        setInput('')

        queryMutation.mutate(text, {
            onSuccess: (response) => {
                const botMessage: ChatMessage = {
                    id: crypto.randomUUID(),
                    text:
                        response?.data?.response ??
                        'No response was returned.',
                    isUser: false,
                    timestamp: new Date(),
                }
                setMessages((prev) => [...prev, botMessage])
            },
            onError: () => {
                const errorMessage: ChatMessage = {
                    id: crypto.randomUUID(),
                    text: 'Something went wrong while contacting the chatbot. Please try again.',
                    isUser: false,
                    timestamp: new Date(),
                }
                setMessages((prev) => [...prev, errorMessage])
            },
        })
    }

    return (
        <div className='h-full flex flex-col'>
            <Card className='flex-1 flex flex-col'>
                <CardHeader>
                    <h1 className='text-xl font-semibold'>Knowledge Base Chat</h1>
                    <p className='text-sm text-muted-foreground'>
                        Ask questions and get answers grounded in this
                        workspace&apos;s knowledge base.
                    </p>
                </CardHeader>
                <Separator />
                <CardContent className='flex-1 flex flex-col p-0'>
                    <ScrollArea className='flex-1 p-4 min-h-[calc(100vh-300px)] max-h-[calc(100vh-300px)]'>
                        {messages.length === 0 && !isSending ? (
                            <div className='h-full flex flex-col items-center justify-center text-center text-muted-foreground py-16'>
                                <Bot className='h-10 w-10 mb-3 opacity-60' />
                                <p className='text-sm'>
                                    {currentWorkspaceId
                                        ? 'Start the conversation by asking a question below.'
                                        : 'Select a workspace to start chatting.'}
                                </p>
                            </div>
                        ) : (
                            <div className='space-y-4'>
                                {messages.map((message) => (
                                    <div
                                        key={message.id}
                                        className={`flex gap-2 ${
                                            message.isUser
                                                ? 'justify-end'
                                                : 'justify-start'
                                        }`}
                                    >
                                        {!message.isUser && (
                                            <div className='flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted'>
                                                <Bot className='h-4 w-4' />
                                            </div>
                                        )}
                                        <div
                                            className={`max-w-[80%] rounded-lg p-3 ${
                                                message.isUser
                                                    ? 'bg-primary text-primary-foreground'
                                                    : 'bg-muted'
                                            }`}
                                        >
                                            <p className='text-sm whitespace-pre-wrap'>
                                                {message.text}
                                            </p>
                                            <p className='text-xs mt-1 opacity-80'>
                                                {message.timestamp.toLocaleTimeString()}
                                            </p>
                                        </div>
                                        {message.isUser && (
                                            <div className='flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground'>
                                                <User className='h-4 w-4' />
                                            </div>
                                        )}
                                    </div>
                                ))}
                                {isSending && (
                                    <div className='flex gap-2 justify-start'>
                                        <div className='flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-muted'>
                                            <Bot className='h-4 w-4' />
                                        </div>
                                        <div className='max-w-[80%] rounded-lg p-3 bg-muted flex items-center gap-2'>
                                            <Loader2 className='h-4 w-4 animate-spin' />
                                            <span className='text-sm text-muted-foreground'>
                                                Thinking...
                                            </span>
                                        </div>
                                    </div>
                                )}
                                <div ref={scrollAnchorRef} />
                            </div>
                        )}
                    </ScrollArea>
                    <form onSubmit={handleSubmit} className='p-4 border-t'>
                        <div className='flex gap-2'>
                            <Input
                                value={input}
                                onChange={(event) => setInput(event.target.value)}
                                placeholder={
                                    currentWorkspaceId
                                        ? 'Type your message...'
                                        : 'Select a workspace first'
                                }
                                disabled={!currentWorkspaceId || isSending}
                                className='flex-1'
                            />
                            <Button type='submit' size='icon' disabled={!canSend}>
                                {isSending ? (
                                    <Loader2 className='h-4 w-4 animate-spin' />
                                ) : (
                                    <Send className='h-4 w-4' />
                                )}
                            </Button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    )
}
