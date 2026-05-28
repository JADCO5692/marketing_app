import { useState } from "react"
import {
  useResearchLogs, useResearchQueue, useCancelResearch,
  useCancelAllResearch, useTogglePause, useRetryFailed,
} from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import {
  RefreshCw, ChevronLeft, ChevronRight, CheckCircle2, XCircle,
  X, Loader2, Pause, Play, XOctagon,
} from "lucide-react"

const SOURCE_OPTIONS = ["", "serper", "playwright", "hunter", "claude", "gemini", "openai", "ai"]

function StatusIcon({ success }: { success: boolean }) {
  return success
    ? <CheckCircle2 size={14} className="text-success-700" />
    : <XCircle size={14} className="text-danger-700" />
}

function formatDateTime(iso: string) {
  const d = new Date(iso)
  return d.toLocaleString(undefined, {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit", second: "2-digit",
  })
}

function formatDuration(ms: number | null | undefined) {
  if (ms == null) return "—"
  if (ms < 1000) return `${ms}ms`
  return `${(ms / 1000).toFixed(1)}s`
}

function QueuePanel() {
  const { data } = useResearchQueue()
  const cancel = useCancelResearch()
  const cancelAll = useCancelAllResearch()
  const togglePause = useTogglePause()

  const items = data?.items ?? []
  const paused: boolean = data?.paused ?? false

  if (items.length === 0 && !paused) return null

  const borderColor = paused ? "border-slate-300" : "border-amber-200"
  const bgColor = paused ? "bg-slate-50" : "bg-amber-50"
  const dividerColor = paused ? "divide-slate-200" : "divide-amber-100"
  const headerBorder = paused ? "border-slate-300" : "border-amber-200"

  return (
    <div className={`rounded-xl border ${borderColor} ${bgColor} mb-6`}>
      <div className={`flex items-center justify-between px-4 py-3 border-b ${headerBorder}`}>
        <div className="flex items-center gap-2">
          {paused
            ? <Pause size={14} className="text-slate-500" />
            : <Loader2 size={14} className="animate-spin text-amber-600" />
          }
          <span className="text-sm font-medium text-slate-700">
            {paused
              ? `Research paused — ${items.length} lead${items.length !== 1 ? "s" : ""} in queue`
              : `Research Queue — ${items.length} lead${items.length !== 1 ? "s" : ""} processing`
            }
          </span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            disabled={togglePause.isPending}
            onClick={() => togglePause.mutate(!paused)}
          >
            {paused ? <><Play size={13} /> Resume</> : <><Pause size={13} /> Pause All</>}
          </Button>
          {items.length > 0 && (
            <Button
              size="sm"
              variant="outline"
              className="text-danger-700 border-danger-700/30 hover:bg-danger-100"
              disabled={cancelAll.isPending}
              onClick={() => cancelAll.mutate()}
            >
              <XOctagon size={13} /> Cancel All
            </Button>
          )}
        </div>
      </div>
      {items.length > 0 && (
        <ul className={`divide-y ${dividerColor}`}>
          {items.map((item: any) => (
            <li key={item.id} className="flex items-center justify-between px-4 py-2.5 text-sm">
              <div>
                <span className="font-medium text-slate-800">{item.name || item.email || "—"}</span>
                {item.company_name && (
                  <span className="text-slate-500 ml-1.5">@ {item.company_name}</span>
                )}
                {item.job_title && (
                  <span className="text-xs text-slate-400 ml-1.5">· {item.job_title}</span>
                )}
              </div>
              <div className="flex items-center gap-3 shrink-0">
                <span className="text-xs text-slate-400">{formatDateTime(item.queued_at)}</span>
                <button
                  title="Cancel this lead"
                  disabled={cancel.isPending}
                  onClick={() => cancel.mutate(item.id)}
                  className="rounded p-1 hover:bg-red-50 text-slate-400 hover:text-danger-700 transition-colors"
                >
                  <X size={13} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

export function Research() {
  const [page, setPage] = useState(1)
  const [source, setSource] = useState("")
  const [successOnly, setSuccessOnly] = useState<string>("")
  const [expanded, setExpanded] = useState<string | null>(null)

  const { data, isLoading } = useResearchLogs({
    page,
    limit: 25,
    source: source || undefined,
    success: successOnly !== "" ? successOnly === "true" : undefined,
  })
  const retryFailed = useRetryFailed()

  const logs = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.ceil(total / 25)

  return (
    <div className="p-6 max-w-6xl">
      <QueuePanel />
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Research Logs</h1>
          <p className="text-sm text-slate-500 mt-0.5">{total} log entries</p>
        </div>
        <Button
          size="sm"
          variant="outline"
          onClick={() => retryFailed.mutate()}
          disabled={retryFailed.isPending}
        >
          <RefreshCw size={13} className={retryFailed.isPending ? "animate-spin" : ""} />
          Retry failed
        </Button>
      </div>

      {/* Filters */}
      <div className="flex gap-3 mb-4">
        <select
          value={source}
          onChange={(e) => { setSource(e.target.value); setPage(1) }}
          className="rounded-lg border px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-900"
        >
          {SOURCE_OPTIONS.map((s) => (
            <option key={s} value={s}>{s || "All sources"}</option>
          ))}
        </select>
        <select
          value={successOnly}
          onChange={(e) => { setSuccessOnly(e.target.value); setPage(1) }}
          className="rounded-lg border px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-900"
        >
          <option value="">All</option>
          <option value="true">Success only</option>
          <option value="false">Failed only</option>
        </select>
      </div>

      <div className="rounded-xl border bg-white overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-slate-50 text-xs font-medium text-slate-500">
              <th className="px-4 py-3 text-left w-6"></th>
              <th className="px-4 py-3 text-left">Lead</th>
              <th className="px-4 py-3 text-left">Source</th>
              <th className="px-4 py-3 text-right">Tokens</th>
              <th className="px-4 py-3 text-right">Cost</th>
              <th className="px-4 py-3 text-right">Duration</th>
              <th className="px-4 py-3 text-left">Created At</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && (
              <tr><td colSpan={7} className="py-12 text-center text-sm text-slate-400">Loading…</td></tr>
            )}
            {!isLoading && logs.length === 0 && (
              <tr><td colSpan={7} className="py-12 text-center text-sm text-slate-400">No logs found</td></tr>
            )}
            {logs.map((log: any) => (
              <>
                <tr
                  key={log.id}
                  onClick={() => setExpanded(expanded === log.id ? null : log.id)}
                  className="border-b cursor-pointer hover:bg-slate-50 transition-colors"
                >
                  <td className="px-4 py-3">
                    <StatusIcon success={log.success} />
                  </td>
                  <td className="px-4 py-3 text-slate-700">
                    {log.lead?.first_name} {log.lead?.last_name}
                    {log.lead?.email && <div className="text-xs text-slate-400">{log.lead.email}</div>}
                  </td>
                  <td className="px-4 py-3">
                    <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{log.source}</span>
                  </td>
                  <td className="px-4 py-3 text-right text-slate-500">{log.tokens_used ?? "—"}</td>
                  <td className="px-4 py-3 text-right text-slate-500">
                    {log.cost_usd != null ? `$${log.cost_usd.toFixed(4)}` : "—"}
                  </td>
                  <td className="px-4 py-3 text-right text-slate-500 tabular-nums">
                    {formatDuration(log.duration_ms)}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400 whitespace-nowrap">
                    {formatDateTime(log.created_at)}
                  </td>
                </tr>
                {expanded === log.id && (
                  <tr key={`${log.id}-detail`} className="border-b bg-slate-50">
                    <td colSpan={7} className="px-4 py-3">
                      {log.error && (
                        <p className="text-xs text-danger-700 mb-2">Error: {log.error}</p>
                      )}
                      {log.raw_response && (
                        <pre className="text-xs text-slate-600 whitespace-pre-wrap max-h-48 overflow-y-auto">
                          {typeof log.raw_response === "string"
                            ? log.raw_response
                            : JSON.stringify(log.raw_response, null, 2)}
                        </pre>
                      )}
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
          <span>Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
              <ChevronLeft size={14} />
            </Button>
            <Button size="sm" variant="outline" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
              <ChevronRight size={14} />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
