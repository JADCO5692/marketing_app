import { useState } from "react"
import { useAppLogs } from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import { RefreshCw, Play, Pause } from "lucide-react"
import { formatDate } from "@/lib/utils"

const LEVELS = ["ALL", "INFO", "WARNING", "ERROR", "CRITICAL"]

const LEVEL_STYLE: Record<string, string> = {
  DEBUG:    "bg-slate-100 text-slate-500",
  INFO:     "bg-blue-50 text-blue-700",
  WARNING:  "bg-amber-50 text-amber-700",
  ERROR:    "bg-danger-100 text-danger-700",
  CRITICAL: "bg-red-200 text-red-800 font-bold",
}

function LevelBadge({ level }: { level: string }) {
  return (
    <span className={`rounded px-1.5 py-0.5 text-xs font-mono font-medium shrink-0 ${LEVEL_STYLE[level] ?? "bg-slate-100 text-slate-500"}`}>
      {level}
    </span>
  )
}

export function AppLogs() {
  const [level, setLevel] = useState("ALL")
  const [autoRefresh, setAutoRefresh] = useState(true)

  const { data: logs, isLoading, refetch, isFetching } = useAppLogs(
    { level: level === "ALL" ? undefined : level, limit: 200 },
    autoRefresh,
  )

  const entries = (logs ?? []) as Array<{
    id: number
    level: string
    logger: string
    message: string
    created_at: string
  }>

  return (
    <div className="p-6 max-w-6xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Application Logs</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Last {entries.length} entries · in-memory, resets on container restart
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoRefresh((v) => !v)}
            className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors ${
              autoRefresh
                ? "border-brand-900 bg-brand-900/5 text-brand-900"
                : "border-slate-200 text-slate-500 hover:bg-slate-50"
            }`}
          >
            {autoRefresh ? <Pause size={12} /> : <Play size={12} />}
            {autoRefresh ? "Live" : "Paused"}
          </button>
          <Button size="sm" variant="outline" onClick={() => refetch()} disabled={isFetching}>
            <RefreshCw size={13} className={isFetching ? "animate-spin" : ""} /> Refresh
          </Button>
        </div>
      </div>

      {/* Level filter */}
      <div className="flex gap-1 mb-4">
        {LEVELS.map((l) => (
          <button
            key={l}
            onClick={() => setLevel(l)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              level === l
                ? "bg-brand-900 text-white"
                : "bg-slate-100 text-slate-500 hover:bg-slate-200"
            }`}
          >
            {l}
          </button>
        ))}
      </div>

      {/* Log table */}
      <div className="rounded-xl border bg-white overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-xs font-mono">
            <thead>
              <tr className="border-b bg-slate-50 text-slate-400 font-sans font-medium text-left">
                <th className="px-4 py-2.5 whitespace-nowrap">Time</th>
                <th className="px-4 py-2.5">Level</th>
                <th className="px-4 py-2.5">Logger</th>
                <th className="px-4 py-2.5 w-full">Message</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr><td colSpan={4} className="py-10 text-center text-slate-400 font-sans text-sm">Loading…</td></tr>
              )}
              {!isLoading && entries.length === 0 && (
                <tr><td colSpan={4} className="py-10 text-center text-slate-400 font-sans text-sm">No log entries yet</td></tr>
              )}
              {entries.map((entry) => (
                <tr key={entry.id} className="border-b hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-2 text-slate-400 whitespace-nowrap">
                    {new Date(entry.created_at).toLocaleTimeString("en-US", {
                      hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false,
                    })}
                  </td>
                  <td className="px-4 py-2">
                    <LevelBadge level={entry.level} />
                  </td>
                  <td className="px-4 py-2 text-slate-400 whitespace-nowrap max-w-[180px] truncate">
                    {entry.logger}
                  </td>
                  <td className="px-4 py-2 text-slate-700 break-all">
                    {entry.message}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
