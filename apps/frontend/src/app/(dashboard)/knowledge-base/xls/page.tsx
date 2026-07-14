import { FileUploadPage } from "@/components/knowledge-base/file-upload-page"

export default function KnowledgeBaseXLSPage() {
  return (
    <FileUploadPage
      title="CSV and Spreadsheets"
      description="Upload CSV, XLS, or XLSX files and index their rows for workspace chat."
      accept=".csv,.xls,.xlsx,text/csv,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      uploadLabel="Upload File"
      visibleTypes={["csv", "xlsx"]}
      emptyLabel="No CSV or spreadsheet files found"
    />
  )
}
