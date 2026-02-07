"use client";

import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { BotMessageSquare, Send, X } from "lucide-react";
import { cn } from "@/lib/utils";
import { defaultTheme } from "@/lib/constants/data";
import { ThemeConfig } from "@/types/config";
import { useCurrentWorkspace } from "@/stores/workspace-store";
import { useTheme } from "@/hooks/use-theme";

const ChatMessage = ({ 
  text, 
  isUser, 
  timestamp, 
  primaryColor,
  secondaryColor,
  textColor
}: { 
  text: string, 
  isUser: boolean, 
  timestamp: Date,
  primaryColor: string,
  secondaryColor: string,
  textColor: string
}) => {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div 
        className={`max-w-[80%] rounded-lg p-3`}
        style={{
          backgroundColor: isUser ? primaryColor : secondaryColor,
          color: isUser ? '#FFFFFF' : textColor
        }}
      >
        <p className="text-sm">{text}</p>
        <p className="text-xs mt-1 opacity-80">{timestamp.toLocaleTimeString()}</p>
      </div>
    </div>
  );
};

const ChatbotPreview = ({ config, setConfig }: { config: ThemeConfig, setConfig: (name: string, value: string | boolean) => void }) => {
  const [messages, setMessages] = useState([
    {
      text: "Hello! How can I help you today?",
      isUser: false,
      timestamp: new Date(Date.now() - 60000)
    },
    {
      text: "I'm looking for some information about your services.",
      isUser: true,
      timestamp: new Date(Date.now() - 30000)
    },
    {
      text: "Of course! I'd be happy to tell you about our services. We offer comprehensive solutions for businesses of all sizes.",
      isUser: false,
      timestamp: new Date()
    }
  ]);
  
  const [inputValue, setInputValue] = useState("");

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;
    
    // Add user message
    const newUserMessage = {
      text: inputValue,
      isUser: true,
      timestamp: new Date()
    };
    
    setMessages([...messages, newUserMessage]);
    setInputValue("");
    
    // Simulate bot response after a delay
    setTimeout(() => {
      const botResponse = {
        text: "Thanks for your message! This is a preview of how the chatbot will respond.",
        isUser: false,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
    }, 1000);
  };

  const getPositionStyles = () => {
    switch(config.position) {
      case "top-left":
        return { top: "20px", left: "20px" };
      case "top-right":
        return { top: "20px", right: "20px" };
      case "bottom-left":
        return { bottom: "20px", left: "20px" };
      case "bottom-right":
      default:
        return { bottom: "20px", right: "20px" };
    }
  };

  return (
    <div className="h-full w-full bg-slate-100 relative">
      
      {/* Chatbot UI */}
      <div 
        style={{
          position: "absolute",
          width: config.width,
          height: config.height,
          borderRadius: config.borderRadius,
          backgroundColor: config.theme === "dark" ? "#1F2937" : "white",
          boxShadow: "0 0 10px rgba(0,0,0,0.1)",
          display: "flex",
          flexDirection: "column",
          zIndex: 1000,
          ...getPositionStyles()
        }}
        className="top-18"
      >
        {/* Header */}
        {config.showHeader && (
          <div 
            style={{
              padding: "16px",
              borderBottom: "1px solid #e5e7eb",
              backgroundColor: config.theme === "dark" ? "#374151" : "#F9FAFB"
            }}
            className="flex justify-between items-center"
          >
            <h1 
              style={{ 
                fontSize: "18px", 
                fontWeight: "600",
                color: config.theme === "dark" ? "white" : config.textColor
              }}
            >
              {config.headerText}
            </h1>
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => setConfig("launcher", !config.launcher)}
              aria-label="Close chatbot"
            >
              <X size={16} />
            </Button>
          </div>
        )}
        
        {/* Messages area */}
        <div 
          style={{
            flex: 1,
            padding: "16px",
            overflowY: "auto",
            backgroundColor: config.theme === "dark" ? "#1F2937" : "white",
            color: config.theme === "dark" ? "white" : config.textColor
          }}
        >
          {messages.map((message, index) => (
            <ChatMessage 
              key={index} 
              text={message.text} 
              isUser={message.isUser} 
              timestamp={message.timestamp}
              primaryColor={config.primaryColor}
              secondaryColor={config.theme === "dark" ? "#374151" : config.secondaryColor}
              textColor={config.textColor}
            />
          ))}
        </div>
        
        {/* Input form */}
        <form 
          onSubmit={handleSendMessage}
          className="p-2 border-t border-gray-300"
          style={{
            backgroundColor: config.theme === "dark" ? "#374151" : "#F9FAFB"
          }}
        >
          <div className="flex gap-2">
            <input 
              type="text" 
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder={config.inputPlaceholder}
              className="flex-1 p-2 border border-gray-300 rounded-md bg-white text-black"
              style={{
                backgroundColor: config.theme === "dark" ? "#374151" : "#F9FAFB",
                color: config.theme === "dark" ? "white" : config.textColor
              }}
            />
            <Button 
              type="submit"
              size="icon"
              className="text-white rounded-md"
              style={{
                backgroundColor: config.primaryColor,
              }}
            >
              <Send size={16} />
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default function ThemeSettingsPage() {
  const { getThemeQuery, updateThemeMutation } = useTheme();
  const {data: themeConfig} = getThemeQuery;
  const [config, setConfig] = useState(themeConfig ?? defaultTheme);
  

  if(getThemeQuery?.isLoading) {
    return <div>Loading...</div>;
  }

  if(getThemeQuery?.error) {
    return <div>Error: {getThemeQuery?.error?.message}</div>;
  }

  if(!getThemeQuery?.data) {
    return <div>No data</div>;
  }


  const handleChange = (name: string, value: string | boolean) => {
    setConfig(prev => ({ ...prev, [name]: value }));
  };

  const handleReset = () => {
    setConfig(defaultTheme);
  };

  const handleSave = () => {
    console.log(config);
    updateThemeMutation.mutate(config);
  };

  
//   const generateEmbedCode = () => {
//     return `<script
//   src="${window.location.origin}/chatbot.js"
//   workspaceId-attr="YOUR_WORKSPACE_ID"
//   userId-attr="YOUR_USER_ID"
//   data-theme="${config.theme}"
//   data-position="${config.position}"
//   data-primary-color="${config.primaryColor}"
//   data-secondary-color="${config.secondaryColor}"
//   data-text-color="${config.textColor}"
//   data-header-text="${config.headerText}"
//   data-placeholder="${config.inputPlaceholder}"
//   data-width="${config.width}"
//   data-height="${config.height}"
//   data-border-radius="${config.borderRadius}"
//   data-launcher="${config.launcher}"
//   data-show-header="${config.showHeader}"
//   async
// ></script>`;
//   };
  
//   const copyToClipboard = () => {
//     navigator.clipboard.writeText(generateEmbedCode())
//       .then(() => alert("Embed code copied to clipboard!"))
//       .catch(err => console.error("Failed to copy: ", err));
//   };
  
  return (
    <div className="flex flex-col space-y-8">
      <div className="flex flex-col space-y-2">
        <h1 className="text-2xl font-bold">Chatbot Theme Configuration</h1>
        <p className="text-muted-foreground">Customize your chatbot appearance and generate embed code.</p>
      </div>
      
      <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
        <div className="flex flex-col space-y-6">
          <Tabs defaultValue="appearance">
            <TabsList className="mb-4">
              <TabsTrigger value="appearance">Appearance</TabsTrigger>
              <TabsTrigger value="content">Content</TabsTrigger>
              <TabsTrigger value="layout">Layout</TabsTrigger>
              <TabsTrigger value="behavior">Behavior</TabsTrigger>
            </TabsList>
            
            <TabsContent value="appearance" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Theme & Colors</CardTitle>
                  <CardDescription>Set the visual theme of your chatbot</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="theme">Theme</Label>
                    <Select 
                      value={config.theme} 
                      onValueChange={(value) => handleChange("theme", value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select theme" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="light">Light</SelectItem>
                        <SelectItem value="dark">Dark</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="primaryColor">Primary Color</Label>
                    <div className="flex items-center gap-2">
                      <Input 
                        id="primaryColor" 
                        type="color" 
                        value={config.primaryColor} 
                        onChange={(e) => handleChange("primaryColor", e.target.value)}
                        className="w-12 h-10 p-1"
                      />
                      <Input 
                        type="text" 
                        value={config.primaryColor} 
                        onChange={(e) => handleChange("primaryColor", e.target.value)}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="secondaryColor">Secondary Color</Label>
                    <div className="flex items-center gap-2">
                      <Input 
                        id="secondaryColor" 
                        type="color" 
                        value={config.secondaryColor} 
                        onChange={(e) => handleChange("secondaryColor", e.target.value)}
                        className="w-12 h-10 p-1"
                      />
                      <Input 
                        type="text" 
                        value={config.secondaryColor} 
                        onChange={(e) => handleChange("secondaryColor", e.target.value)}
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="textColor">Text Color</Label>
                    <div className="flex items-center gap-2">
                      <Input 
                        id="textColor" 
                        type="color" 
                        value={config.textColor} 
                        onChange={(e) => handleChange("textColor", e.target.value)}
                        className="w-12 h-10 p-1"
                      />
                      <Input 
                        type="text" 
                        value={config.textColor} 
                        onChange={(e) => handleChange("textColor", e.target.value)}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="content" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Text Content</CardTitle>
                  <CardDescription>Customize chatbot text content</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="headerText">Header Text</Label>
                    <Input 
                      id="headerText" 
                      value={config.headerText} 
                      onChange={(e) => handleChange("headerText", e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="inputPlaceholder">Input Placeholder</Label>
                    <Input 
                      id="inputPlaceholder" 
                      value={config.inputPlaceholder} 
                      onChange={(e) => handleChange("inputPlaceholder", e.target.value)}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="layout" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Size & Position</CardTitle>
                  <CardDescription>Configure chatbot dimensions and position</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="position">Position</Label>
                    <Select 
                      value={config.position} 
                      onValueChange={(value) => handleChange("position", value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select position" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="bottom-right">Bottom Right</SelectItem>
                        <SelectItem value="bottom-left">Bottom Left</SelectItem>
                        <SelectItem value="top-right">Top Right</SelectItem>
                        <SelectItem value="top-left">Top Left</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="width">Width</Label>
                    <Input 
                      id="width" 
                      value={config.width} 
                      onChange={(e) => handleChange("width", e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="height">Height</Label>
                    <Input 
                      id="height" 
                      value={config.height} 
                      onChange={(e) => handleChange("height", e.target.value)}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="borderRadius">Border Radius</Label>
                    <Input 
                      id="borderRadius" 
                      value={config.borderRadius} 
                      onChange={(e) => handleChange("borderRadius", e.target.value)}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="behavior" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Behavior Options</CardTitle>
                  <CardDescription>Configure chatbot behavior</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="launcher">Show Launcher Button</Label>
                    <Switch 
                      id="launcher" 
                      checked={config.launcher}
                      onCheckedChange={(checked) => handleChange("launcher", checked)}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <Label htmlFor="showHeader">Show Header</Label>
                    <Switch 
                      id="showHeader" 
                      checked={config.showHeader}
                      onCheckedChange={(checked) => handleChange("showHeader", checked)}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
          
          {/* <Card>
            <CardHeader>
              <CardTitle>Embed Code</CardTitle>
              <CardDescription>Copy this code to your website</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative">
                <pre className="bg-secondary p-4 rounded-md overflow-x-auto text-xs">
                  {generateEmbedCode()}
                </pre>
                <Button 
                  className="absolute top-2 right-2" 
                  size="sm" 
                  onClick={copyToClipboard}
                >
                  Copy
                </Button>
              </div>
            </CardContent>
          </Card> */}
          <div className="flex gap-2">
            <Button className="w-full" variant="outline" onClick={handleReset}>Reset</Button>
            <Button className="w-full" onClick={handleSave}>Save</Button>
          </div>
        </div>
        
        <div className="min-h-[700px] relative">
          <Card className="absolute inset-0 overflow-hidden">
            <CardHeader>
              <CardTitle>Preview</CardTitle>
              <CardDescription>Live preview of your chatbot</CardDescription>
            </CardHeader>
            <CardContent className="flex-1 p-0">
              {config.launcher && <ChatbotPreview config={config} setConfig={handleChange} />}
            
              <BotMessageSquare style={{ color: config.primaryColor }} className={cn("absolute bottom-10 right-10 size-10 rounded-full cursor-pointer")} onClick={() => handleChange("launcher", !config.launcher)}/>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}