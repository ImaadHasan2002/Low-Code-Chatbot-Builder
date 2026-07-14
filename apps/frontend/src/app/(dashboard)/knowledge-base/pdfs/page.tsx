"use client"

import * as React from "react"
import Link from "next/link"
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
import {
  ArrowUpDown,
  ChevronDown,
  Copy,
  ExternalLink,
  FileText,
  Loader2,
  MessageCircle,
  MoreHorizontal,
  Trash2,
  Upload,
} from "lucide-react"
import { toast } from "sonner"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
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
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { useKnowledgeBase } from "@/hooks/use-knowledge-base"
import { useWorkspaceStore } from "@/stores/workspace-store"
import type { KnowledgeBaseItem } from "@/types/knowledge-base"

function formatDate(value: string) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return "Unknown"
  }

  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

export default function KnowledgeBasePDFsPage() {
  const { currentWorkspaceId } = useWorkspaceStore()
  const {
    uploadFileMutation,
    deleteKnowledgeBaseMutation,
    getPDFsQuery,
  } = useKnowledgeBase()
  const { data, isLoading, isError, isSuccess, error } = getPDFsQuery

  const fileInputRef = React.useRef<HTMLInputElement>(null)
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] =
    React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})

  const tableData = React.useMemo(
    () => (isSuccess && data?.data ? data.data : []),
    [data?.data, isSuccess]
  )

  const copyToClipboard = React.useCallback(async (value: string) => {
    await navigator.clipboard.writeText(value)
    toast.success("Copied")
  }, [])

  const deletePdf = React.useCallback(
    (pdf: KnowledgeBaseItem) => {
      const confirmed = window.confirm(`Delete "${pdf.name}" from this workspace?`)
      if (!confirmed) return

      deleteKnowledgeBaseMutation.mutate(pdf._id)
    },
    [deleteKnowledgeBaseMutation]
  )

  const columns = React.useMemo<ColumnDef<KnowledgeBaseItem>[]>(
    () => [
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
        header: "Name",
        cell: ({ row }) => (
          <Link
            href={`/knowledge-base/pdfs/${row.original._id}`}
            className="flex min-w-0 items-center gap-2 font-medium hover:underline"
          >
            <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
            <span className="truncate">{row.original.name}</span>
          </Link>
        ),
      },
      {
        accessorKey: "type",
        header: "Type",
        cell: () => <Badge variant="secondary">PDF</Badge>,
      },
      {
        accessorKey: "updated_at",
        header: ({ column }) => (
          <Button
            variant="ghost"
            onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          >
            Last Modified
            <ArrowUpDown />
          </Button>
        ),
        cell: ({ row }) => <div>{formatDate(row.original.updated_at)}</div>,
      },
      {
        accessorKey: "created_at",
        header: "Added",
        cell: ({ row }) => <div>{formatDate(row.original.created_at)}</div>,
      },
      {
        id: "actions",
        enableHiding: false,
        cell: ({ row }) => {
          const pdf = row.original
          const isDeleting =
            deleteKnowledgeBaseMutation.isPending &&
            deleteKnowledgeBaseMutation.variables === pdf._id

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
                <DropdownMenuItem asChild>
                  <Link href={`/knowledge-base/pdfs/${pdf._id}`}>
                    <FileText />
                    Details
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <a href={pdf.file_url} target="_blank" rel="noreferrer">
                    <ExternalLink />
                    Open PDF
                  </a>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => copyToClipboard(pdf.file_url)}>
                  <Copy />
                  Copy source URL
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link href="/knowledge-base/chat">
                    <MessageCircle />
                    Chat
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  variant="destructive"
                  disabled={isDeleting}
                  onClick={() => deletePdf(pdf)}
                >
                  {isDeleting ? <Loader2 className="animate-spin" /> : <Trash2 />}
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )
        },
      },
    ],
    [copyToClipboard, deleteKnowledgeBaseMutation, deletePdf]
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

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]

    if (!file) return

    if (!file.name.toLowerCase().endsWith(".pdf")) {
      toast.error("Only PDF files are supported")
      event.target.value = ""
      return
    }

    uploadFileMutation.mutate(file, {
      onSettled: () => {
        event.target.value = ""
      },
    })
  }

  if (!currentWorkspaceId) {
    return (
      <Alert>
        <AlertTitle>No workspace selected</AlertTitle>
        <AlertDescription>
          Create or select a workspace before adding PDF knowledge sources.
        </AlertDescription>
      </Alert>
    )
  }

  return (
    <div className="w-full space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Input
          placeholder="Filter PDFs..."
          value={(table.getColumn("name")?.getFilterValue() as string) ?? ""}
          onChange={(event) =>
            table.getColumn("name")?.setFilterValue(event.target.value)
          }
          className="max-w-sm"
        />
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploadFileMutation.isPending}
          >
            {uploadFileMutation.isPending ? (
              <Loader2 className="animate-spin" />
            ) : (
              <Upload />
            )}
            Upload PDF
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="hidden"
            onChange={handleFileUpload}
          />
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline">
                Columns <ChevronDown />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {table
                .getAllColumns()
                .filter((column) => column.getCanHide())
                .map((column) => (
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
                ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>

      {isError ? (
        <Alert variant="destructive">
          <AlertTitle>Could not load PDFs</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : "Please refresh and try again."}
          </AlertDescription>
        </Alert>
      ) : null}

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
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
              Array.from({ length: 5 }).map((_, i) => (
                <TableRow key={i}>
                  {columns.map((column) => (
                    <TableCell key={column.id ?? String(column.header)}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : table.getRowModel().rows.length ? (
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
                  No PDFs found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2">
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
