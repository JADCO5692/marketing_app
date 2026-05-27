import { useRef, useState } from "react"
import { Upload as UploadIcon, CheckCircle2, AlertCircle, Loader2, FileSpreadsheet, FileText } from "lucide-react"
import { useUploadCsv, useUploadJob } from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

const ACCEPTED_EXTENSIONS = [".csv", ".xlsx", ".xls"]
const ACCEPT_ATTR = ACCEPTED_EXTENSIONS.join(",")

function fileIcon(name: string) {
  if (name.endsWith(".csv")) return <FileText size={14} className="shrink-0 text-slate-400" />
  return <FileSpreadsheet size={14} className="shrink-0 text-emerald-600" />
}

function isAllowed(file: File) {
  const lower = file.name.toLowerCase()
  return ACCEPTED_EXTENSIONS.some((ext) => lower.endsWith(ext))
}

export function Upload() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragOver, setDragOver] = useState(false)
  const [jobId, setJobId] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const upload = useUploadCsv()
  const { data: job } = useUploadJob(jobId)

  function handleFile(file: File) {
    if (!isAllowed(file)) return
    setSelectedFile(file)
    upload.mutate(file, {
      onSuccess: (res) => setJobId(res.data.job_id),
    })
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }

  const isProcessing = job?.status === "processing" || upload.isPending
  const isDone = job?.status === "done"
  const isFailed = job?.status === "failed"

  return (
    <div className="p-8 max-w-2xl">
      <h1 className="text-xl font-semibold text-slate-900 mb-1">Upload Leads</h1>
      <p className="text-sm text-slate-500 mb-6">
        Upload a CSV or Excel file with lead data. Duplicates are detected automatically.
      </p>

      {/* Drop zone */}
      <div
        className={cn(
          "rounded-xl border-2 border-dashed p-12 text-center transition-colors cursor-pointer",
          dragOver ? "border-brand-900 bg-brand-900/5" : "border-slate-200 hover:border-slate-300",
          isProcessing && "pointer-events-none opacity-60"
        )}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <UploadIcon className="mx-auto mb-3 text-slate-400" size={32} />
        <p className="text-sm font-medium text-slate-700">Drop your file here or click to browse</p>
        <div className="mt-2 flex items-center justify-center gap-3 text-xs text-slate-400">
          <span className="flex items-center gap-1">
            <FileText size={12} /> CSV
          </span>
          <span className="text-slate-200">|</span>
          <span className="flex items-center gap-1">
            <FileSpreadsheet size={12} className="text-emerald-500" /> Excel (.xlsx / .xls)
          </span>
        </div>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPT_ATTR}
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f) }}
        />
      </div>

      {/* Status panel */}
      {(isProcessing || isDone || isFailed || upload.isError) && (
        <div className="mt-6 rounded-xl border bg-white p-5 space-y-3">
          {selectedFile && (
            <div className="flex items-center gap-2 text-xs text-slate-500 border-b pb-3">
              {fileIcon(selectedFile.name)}
              <span className="font-medium text-slate-700">{selectedFile.name}</span>
              <span className="ml-auto">{(selectedFile.size / 1024).toFixed(1)} KB</span>
            </div>
          )}

          {isProcessing && (
            <div className="flex items-center gap-3 text-sm text-slate-700">
              <Loader2 size={16} className="animate-spin text-brand-900" />
              Processing… {job ? `${job.processed ?? 0} / ${job.total_rows ?? "?"} rows` : "uploading"}
            </div>
          )}

          {isDone && (
            <div className="flex items-start gap-3">
              <CheckCircle2 size={16} className="mt-0.5 shrink-0 text-success-700" />
              <div className="text-sm">
                <p className="font-medium text-slate-900">Upload complete</p>
                <p className="text-slate-500">
                  {job.stored} inserted · {job.duplicates_found} duplicates skipped · {job.failed_rows} errors
                </p>
              </div>
            </div>
          )}

          {(isFailed || upload.isError) && (
            <div className="flex items-start gap-3">
              <AlertCircle size={16} className="mt-0.5 shrink-0 text-danger-700" />
              <div className="text-sm">
                <p className="font-medium text-slate-900">Upload failed</p>
                <p className="text-slate-500">
                  {job?.errors?.[0] ?? "Unexpected error. Please try again."}
                </p>
              </div>
            </div>
          )}

          {isDone && (
            <Button
              size="sm"
              variant="outline"
              onClick={() => { setJobId(null); setSelectedFile(null); upload.reset() }}
            >
              Upload another file
            </Button>
          )}
        </div>
      )}

      {/* Column reference */}
      <div className="mt-8">
        <h2 className="text-sm font-semibold text-slate-700 mb-3">Expected columns (CSV or first sheet of Excel)</h2>
        <div className="grid grid-cols-2 gap-x-8 gap-y-1.5">
          {[
            ["first_name", "optional"],
            ["last_name", "optional"],
            ["email", "recommended"],
            ["phone", "optional"],
            ["title / job_title", "optional"],
            ["company / company_name", "optional"],
            ["website", "optional"],
            ["linkedin_url", "optional"],
            ["industry", "optional"],
            ["city / state / country", "optional"],
          ].map(([col, note]) => (
            <div key={col} className="flex items-center gap-2 text-xs">
              <code className="rounded bg-slate-100 px-1.5 py-0.5 text-slate-700">{col}</code>
              <span className="text-slate-400">{note}</span>
            </div>
          ))}
        </div>
        <p className="mt-3 text-xs text-slate-400">
          Any extra columns are stored as raw data and available for custom filters.
        </p>
      </div>
    </div>
  )
}
