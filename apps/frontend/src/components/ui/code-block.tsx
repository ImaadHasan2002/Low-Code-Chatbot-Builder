"use client"

import * as React from "react"
import { Check, Copy } from "lucide-react"
import { cn } from "@/lib/utils"

interface CodeBlockProps extends React.HTMLAttributes<HTMLPreElement> {
  language?: string
  code: string
  showLineNumbers?: boolean
}

export function CodeBlock({
  language,
  code,
  showLineNumbers = false,
  className,
  ...props
}: CodeBlockProps) {
  const [copied, setCopied] = React.useState(false)
  const preRef = React.useRef<HTMLPreElement>(null)

  const copyToClipboard = async () => {
    if (!navigator.clipboard || !preRef.current) return
    
    try {
      await navigator.clipboard.writeText(code)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error("Failed to copy code: ", error)
    }
  }

  return (
    <div className="relative group rounded-md max-w-full">
      <pre
        ref={preRef}
        data-slot="code-block"
        className={cn(
          "relative overflow-auto rounded-md border border-border bg-muted p-2 text-sm",
          showLineNumbers && "pl-12",
          "scrollbar-thin scrollbar-thumb-border scrollbar-track-transparent",
          "ring-ring/10 dark:ring-ring/20 dark:outline-ring/40 outline-ring/50 focus-visible:ring-4 focus-visible:outline-1",
          className
        )}
        {...props}
      >
        {showLineNumbers && (
          <div className="absolute left-0 top-4 w-8 select-none border-r border-border text-right text-xs text-muted-foreground">
            {code.split('\n').map((_, i) => (
              <div key={i} className="pr-2">
                {i + 1}
              </div>
            ))}
          </div>
        )}
        <code className={cn("grid", language && `language-${language}`)}>
          {code}
        </code>
      </pre>
      <button
        onClick={copyToClipboard}
        data-slot="copy-button"
        className={cn(
          "absolute right-3 top-3 rounded-md border border-border bg-background p-1.5",
          "text-muted-foreground opacity-0 transition-[opacity,color,box-shadow]",
          "hover:bg-accent hover:text-accent-foreground focus:opacity-100 group-hover:opacity-100",
          "ring-ring/10 dark:ring-ring/20 dark:outline-ring/40 outline-ring/50 focus-visible:ring-4 focus-visible:outline-1",
          "disabled:pointer-events-none disabled:opacity-50"
        )}
        aria-label="Copy code"
      >
        {copied ? <Check className="size-4" /> : <Copy className="size-4" />}
      </button>
      {language && (
        <div 
          data-slot="language-badge"
          className="absolute right-3 bottom-3 rounded px-1.5 py-0.5 text-xs text-muted-foreground bg-muted border border-border"
        >
          {language}
        </div>
      )}
    </div>
  )
}