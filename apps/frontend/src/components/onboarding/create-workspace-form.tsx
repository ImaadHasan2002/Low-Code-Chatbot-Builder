"use client"

import { useRouter } from "next/navigation"
import { SubmitHandler, useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { createWorkspaceSchema, type CreateWorkspaceInput } from "@/lib/validations/workspace"
import { useWorkspace } from "@/hooks/use-workspace"

export function CreateWorkspaceForm() {
  const router = useRouter()
  const { createWorkspaceMutation } = useWorkspace()

  const form = useForm<CreateWorkspaceInput>({
    resolver: zodResolver(createWorkspaceSchema),
    defaultValues: {
      name: "",
      website_url: "",
      crawl_max_pages: 25,
      crawl_max_depth: 2,
    }
  })

  const onSubmit: SubmitHandler<CreateWorkspaceInput> = async (data) => {
      await createWorkspaceMutation.mutateAsync({
        ...data,
        website_url: data.website_url || undefined,
      })
      router.push("/dashboard");
  }

  return (
    <div className="flex w-full flex-col gap-6">
      <div className="flex flex-col gap-2 text-center">
        <h1 className="text-2xl font-bold">Create your workspace</h1>
        <p className="text-balance text-sm text-muted-foreground">
          Create a workspace to get started with BotCraft. You can add team members later.
        </p>
      </div>
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="grid gap-6">
          {/* TODO: Add logo upload */}
          {/* <div className="flex justify-center">
            <FormField
              control={form.control}
              name="logo"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <WorkspaceAvatar
                      icon={field.value}
                      onChange={field.onChange}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div> */}
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Workspace Name</FormLabel>
                <FormControl>
                  <Input placeholder="Botcraft" {...field} />
                </FormControl>
                <FormDescription>
                  This is the name of your organization&apos;s workspace
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="website_url"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Website URL</FormLabel>
                <FormControl>
                  <Input placeholder="https://example.com" {...field} />
                </FormControl>
                <FormDescription>
                  BotCraft will start crawling this site after the workspace is created.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
          <div className="grid gap-4 sm:grid-cols-2">
            <FormField
              control={form.control}
              name="crawl_max_pages"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Max Pages</FormLabel>
                  <FormControl>
                    <Input type="number" min={1} max={500} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="crawl_max_depth"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Depth</FormLabel>
                  <FormControl>
                    <Input type="number" min={0} max={10} {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>
          <Button
            type="submit"
            className="w-full"
            disabled={createWorkspaceMutation.isPending}
          >
            {createWorkspaceMutation.isPending ? "Creating..." : "Create Workspace"}
          </Button>
        </form>
      </Form>
    </div>
  )
}
