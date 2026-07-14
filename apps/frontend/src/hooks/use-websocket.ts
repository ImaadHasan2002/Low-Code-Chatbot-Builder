import { useEffect, useState, useCallback, useRef } from "react";

interface Conversation {
    id: string
    text: string
    isUser: boolean
    timestamp: Date
}

export function useWebSocket({ path, workspaceId }: { path: string, workspaceId?: string | null }) {
    const [conversation, setConversation] = useState<Conversation[]>([]);
    const [isConnected, setIsConnected] = useState(false);
    const socketRef = useRef<WebSocket | null>(null);

    const sendMessage = useCallback((message: string) => {
        const socket = socketRef.current;
        if (socket && socket.readyState === WebSocket.OPEN) {
            const newMessage: Conversation = {
                id: crypto.randomUUID(),
                text: message,
                isUser: true,
                timestamp: new Date(),
            };
            setConversation(prev => [...prev, newMessage]);
            socket.send(message);
        } else {
            console.error("Socket not connected");
        }
    }, []);

    const disconnect = useCallback(() => {
        socketRef.current?.close();
        socketRef.current = null;
        setIsConnected(false);
    }, []);

    useEffect(() => {
        const wsBase = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
        const wsPath = `${wsBase}/api/v1/${path}`;
        const wsUrl = workspaceId ? `${wsPath}?workspace_id=${workspaceId}` : wsPath;

        const socket = new WebSocket(wsUrl);
        socketRef.current = socket;

        socket.onopen = () => setIsConnected(true);
        socket.onmessage = (event) => {
            const newMessage: Conversation = {
                id: crypto.randomUUID(),
                text: event.data,
                isUser: false,
                timestamp: new Date(),
            };
            setConversation(prev => [...prev, newMessage]);
        };
        socket.onclose = () => setIsConnected(false);
        socket.onerror = (event) => console.log("websocket error", event);

        return () => {
            socket.close();
            socketRef.current = null;
        };
    }, [path, workspaceId]);

    return { isConnected, disconnect, sendMessage, conversation };
}
