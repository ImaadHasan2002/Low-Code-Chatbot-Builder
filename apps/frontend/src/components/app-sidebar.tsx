"use client"

import * as React from "react"
import {
  BookOpen,
  Bot,
  LifeBuoy,
  Send,
  Settings2,
  SquareTerminal,
  BarChart,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavSecondary } from "@/components/nav-secondary"
import { NavUser } from "@/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
} from "@/components/ui/sidebar"
import { WorkspaceSwitcher } from "@/components/workspace-switcher"
import { useWorkspace } from "@/hooks/use-workspace"
const data = {
  user: {
    name: "Imaad Hasan",
    email: "imaadhasan16@gmail.com",
    avatar: "/avatars/shadcn.jpg",
  },
  navMain: [
    {
      title: "Analytics",
      url: "/analytics",
      icon: BarChart,
      isActive: false,
      // items: [
      //   {
      //     title: "History",
      //     url: "#",
      //   },
      //   {
      //     title: "Starred",
      //     url: "#",
      //   },
      //   {
      //     title: "Settings",
      //     url: "#",
      //   },
      // ],
    },
    {
      title: "Playground",
      url: "/playground",
      icon: SquareTerminal,
      isActive: false,
      // items: [
      //   {
      //     title: "History",
      //     url: "#",
      //   },
      //   {
      //     title: "Starred",
      //     url: "#",
      //   },
      //   {
      //     title: "Settings",
      //     url: "#",
      //   },
      // ],
    },
    {
      title: "Knowledge Base",
      url: "/knowledge-base",
      icon: Bot,
      isActive: true,
      items: [
        {
          title: "PDFs",
          url: "/knowledge-base/pdfs",
        },
        {
          title: "Links",
          url: "/knowledge-base/links",
        },
        {
          title: "Xls",
          url: "/knowledge-base/xls",
        },
        {
          title: "Chat",
          url: "/knowledge-base/chat",
        },
        {
          title: "Images",
          url: "/knowledge-base/images",
        },
      ],
    },
    {
      title: "Settings",
      url: "/settings",
      icon: Settings2,
      items: [
        {
          title: "General",
          url: "/settings/general",
        },
        {
          title: "Advanced",
          url: "/settings/advanced",
        },
        {
          title: "Theme",
          url: "/settings/theme",
        },
        {
          title: "Billing",
          url: "/settings/billing",
        },
        {
          title: "Limits",
          url: "/settings/limits",
        },
      ],
    },
  ],
  navSecondary: [
    {
      title: "Support",
      url: "#",
      icon: LifeBuoy,
    },
    {
      title: "Feedback",
      url: "#",
      icon: Send,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const { getWorkspacesQuery } = useWorkspace();
  const { data: workspaces } = getWorkspacesQuery;

  return (
    <Sidebar variant="inset" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <WorkspaceSwitcher workspaces={workspaces || []} />
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavSecondary items={data.navSecondary} className="mt-auto" />
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={data.user} />
      </SidebarFooter>
    </Sidebar>
  )
}
