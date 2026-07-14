import { z } from "zod"

export const createWorkspaceSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters").max(50, "Name must be less than 50 characters"),
  website_url: z.string().url("Enter a valid URL").or(z.literal("")).optional(),
  crawl_max_pages: z.coerce.number().int().min(1).max(500).default(25),
  crawl_max_depth: z.coerce.number().int().min(0).max(10).default(2),
})

export type CreateWorkspaceInput = z.infer<typeof createWorkspaceSchema>
