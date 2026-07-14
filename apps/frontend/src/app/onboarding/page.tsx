import Link from "next/link"
import { GalleryVerticalEnd } from "lucide-react"

import { CreateWorkspaceForm } from "@/components/onboarding/create-workspace-form"

export default function OnboardingPage() {
  return (
    <div className="min-h-svh">
      <div className="flex flex-col gap-4 p-6 md:p-10">
        <div className="flex justify-center gap-2 md:justify-start">
          <Link href="/" className="flex items-center gap-2 font-medium">
            <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary text-primary-foreground">
              <GalleryVerticalEnd className="size-4" />
            </div>
            BotCraft
          </Link>
        </div>
        <div className="mx-auto flex w-full max-w-xl flex-1 items-center justify-center">
          <CreateWorkspaceForm />
        </div>
      </div>
    </div>
  )
}
