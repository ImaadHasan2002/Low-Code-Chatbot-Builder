"use client"

import * as React from "react"
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"
import { ChevronDown, Loader2, MoreHorizontal, Trash2 } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import { Label } from "@/components/ui/label"
 
import { useKnowledgeBase } from "@/hooks/use-knowledge-base"
import type { KnowledgeBaseItem } from "@/types/knowledge-base"

type DeleteFn = (id: string) => void
type DeletingId = string | undefined

function makeColumns(onDelete: DeleteFn, deletingId: DeletingId): ColumnDef<KnowledgeBaseItem>[] {
  return [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "name",
    header: "Page",
    cell: ({ row }) => (
      <div className="max-w-xs truncate font-medium">{row.original.name || row.original.file_url}</div>
    ),
  },
  {
    accessorKey: "file_url",
    header: "URL",
    cell: ({ row }) => (
      <div className="max-w-xs truncate text-muted-foreground text-xs">{row.getValue("file_url")}</div>
    ),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => (
      <Badge variant={row.original.status === "failed" ? "destructive" : "secondary"}>
        {row.original.status ?? "indexed"}
      </Badge>
    ),
  },
  {
    id: "actions",
    enableHiding: false,
    cell: ({ row }) => {
      const knowledgeBase = row.original
      const isDeleting = deletingId === knowledgeBase._id

      return (
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-8 w-8 p-0">
              <span className="sr-only">Open menu</span>
              <MoreHorizontal />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuLabel>Actions</DropdownMenuLabel>
            <DropdownMenuItem
              onClick={() => navigator.clipboard.writeText(knowledgeBase._id)}
            >
              Copy knowledge source ID
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem asChild>
              <a href={knowledgeBase.file_url} target="_blank" rel="noreferrer">
                Open link
              </a>
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem
              variant="destructive"
              disabled={isDeleting}
              onClick={() => onDelete(knowledgeBase._id)}
            >
              {isDeleting ? <Loader2 className="animate-spin" /> : <Trash2 />}
              Delete
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )
    },
  },
]}

export default function KnowledgeBaseLinksPage() {
  const { getLinksQuery, getCrawlJobsQuery, crawlWebsiteMutation, deleteKnowledgeBaseMutation } = useKnowledgeBase()
  const { data, isLoading, isError, isSuccess } = getLinksQuery
  const crawlJobs = React.useMemo(
    () => getCrawlJobsQuery.data?.data.jobs ?? [],
    [getCrawlJobsQuery.data?.data.jobs]
  )

  const prevCrawlJobsRef = React.useRef(crawlJobs)
  React.useEffect(() => {
    const prevJobs = prevCrawlJobsRef.current
    const justCompleted = crawlJobs.some(
      (job) =>
        job.status === "completed" &&
        prevJobs.find((p) => p.job_id === job.job_id && p.status !== "completed")
    )
    if (justCompleted) {
      getLinksQuery.refetch()
    }
    prevCrawlJobsRef.current = crawlJobs
  }, [crawlJobs, getLinksQuery])

  const handleDelete = React.useCallback(
    (id: string) => {
      if (!window.confirm("Remove this page from the knowledge base?")) return
      deleteKnowledgeBaseMutation.mutate(id)
    },
    [deleteKnowledgeBaseMutation]
  )

  const [baseUrl, setBaseUrl] = React.useState<string>("")
  const [maxPages, setMaxPages] = React.useState<number>(25)
  const [maxDepth, setMaxDepth] = React.useState<number>(2)
  const [includePaths, setIncludePaths] = React.useState<string>("")
  const [excludePaths, setExcludePaths] = React.useState<string>("")
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
    []
  )
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})

  const tableData = isSuccess && data?.data ? data.data.links : []

  const columns = React.useMemo(
    () => makeColumns(handleDelete, deleteKnowledgeBaseMutation.isPending ? deleteKnowledgeBaseMutation.variables : undefined),
    [handleDelete, deleteKnowledgeBaseMutation.isPending, deleteKnowledgeBaseMutation.variables]
  )

  const table = useReactTable({
    data: tableData,
    columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onColumnVisibilityChange: setColumnVisibility,
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      columnVisibility,
      rowSelection,
    },
  })

  const splitPaths = (value: string) =>
    value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean)

  const handleStartCrawl = () => {
    if (!baseUrl) return
    crawlWebsiteMutation.mutate({
      base_url: baseUrl,
      max_pages: maxPages,
      max_depth: maxDepth,
      include_paths: splitPaths(includePaths),
      exclude_paths: splitPaths(excludePaths),
    })
  }

  return (
    <div className="w-full space-y-4">
      {crawlJobs.length ? (
        <div className="rounded-md border p-3">
          <div className="mb-2 text-sm font-medium">Recent crawl status</div>
          <div className="grid gap-2 md:grid-cols-2">
            {crawlJobs.slice(0, 4).map((job) => (
              <div key={job.job_id} className="flex items-center justify-between gap-3 rounded-md bg-muted/40 px-3 py-2">
                <div className="min-w-0">
                  <div className="truncate text-sm">{job.payload.base_url ?? "Website crawl"}</div>
                  <div className="text-xs text-muted-foreground">
                    {job.message ?? `${job.processed_items}/${job.total_items || 0} pages`}
                  </div>
                </div>
                <Badge variant={job.status === "failed" ? "destructive" : "secondary"}>
                  {job.status}
                </Badge>
              </div>
            ))}
          </div>
        </div>
      ) : null}

      <div className="flex items-center justify-between py-4">
        <Input
          placeholder="Filter links..."
          value={(table.getColumn("name")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("name")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <div className="flex items-center gap-2">
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline">Crawl Website</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Crawl Website</DialogTitle>
                <DialogDescription>
                  Index pages from a website into this workspace.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="base-url">Base URL</Label>
                  <Input
                    id="base-url"
                    placeholder="https://example.com"
                    value={baseUrl}
                    onChange={(event) => setBaseUrl(event.target.value)}
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div className="grid gap-2">
                    <Label htmlFor="max-pages">Max pages</Label>
                    <Input
                      id="max-pages"
                      type="number"
                      min={1}
                      max={500}
                      value={maxPages}
                      onChange={(event) => setMaxPages(Number(event.target.value))}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="max-depth">Depth</Label>
                    <Input
                      id="max-depth"
                      type="number"
                      min={0}
                      max={10}
                      value={maxDepth}
                      onChange={(event) => setMaxDepth(Number(event.target.value))}
                    />
                  </div>
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="include-paths">Include paths</Label>
                  <Input
                    id="include-paths"
                    placeholder="/docs, /pricing"
                    value={includePaths}
                    onChange={(event) => setIncludePaths(event.target.value)}
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="exclude-paths">Exclude paths</Label>
                  <Input
                    id="exclude-paths"
                    placeholder="/blog, /legal"
                    value={excludePaths}
                    onChange={(event) => setExcludePaths(event.target.value)}
                  />
                </div>
              </div>
              <DialogFooter className="sm:justify-start">
                <DialogClose asChild>
                  <Button type="button" variant="secondary">Close</Button>
                </DialogClose>
                <Button
                  type="submit"
                  onClick={handleStartCrawl}
                  disabled={crawlWebsiteMutation.isPending}
                >
                  {crawlWebsiteMutation.isPending ? <Loader2 className="animate-spin" /> : null}
                  Start Crawl
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                Columns <ChevronDown />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {table
                ?.getAllColumns()
                ?.filter((column) => column.getCanHide())
                ?.map((column) => {
                  return (
                    <DropdownMenuCheckboxItem
                    key={column.id}
                    className="capitalize"
                    checked={column.getIsVisible()}
                    onCheckedChange={(value) =>
                      column.toggleVisibility(!!value)
                    }
                    >
                      {column.id}
                    </DropdownMenuCheckboxItem>
                  )
                })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups()?.map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers?.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {isLoading ? (
              // Loading state
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {columns.map((_, j) => (
                    <TableCell key={j}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : isError ? (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  Error loading data
                </TableCell>
              </TableRow>
            ) : table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <div className="flex-1 text-sm text-muted-foreground">
          {table.getFilteredSelectedRowModel().rows.length} of{" "}
          {table.getFilteredRowModel().rows.length} row(s) selected.
        </div>
        <div className="space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.previousPage()}
            disabled={!table.getCanPreviousPage()}
          >
            Previous
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => table.nextPage()}
            disabled={!table.getCanNextPage()}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  )
}
