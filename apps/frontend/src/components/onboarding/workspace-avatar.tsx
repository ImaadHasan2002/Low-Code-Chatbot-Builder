"use client"

import * as React from "react"
import { Frame, type LucideIcon, UserRound, Wrench, Home,  } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const workspaceIcons = {
  Frame,
  UserRound,
  Wrench,
  Home,
}

interface WorkspaceAvatarProps extends Omit<React.HTMLAttributes<HTMLButtonElement>, 'onChange'> {
  icon?: LucideIcon
  onChange?: (icon: LucideIcon) => void
}

export function WorkspaceAvatar({
  icon = Frame,
  onChange,
  className,
  ...props
}: WorkspaceAvatarProps) {
  const Icon = icon

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="outline"
          className={cn(
            "size-16 rounded-lg border-2 border-dashed p-4 hover:border-primary",
            className
          )}
          {...props}
        >
          <Icon className="size-full" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="center" className="w-48">
        <div className="grid grid-cols-4 gap-2 p-2">
          {Object.entries(workspaceIcons).map(([name, IconComponent]) => (
            <DropdownMenuItem
              key={name}
              className="flex h-10 w-10 items-center justify-center rounded-md p-0 focus:bg-primary focus:text-primary-foreground"
              onSelect={() => onChange?.(IconComponent)}
            >
              <IconComponent className="size-5" />
            </DropdownMenuItem>
          ))}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  )
} 