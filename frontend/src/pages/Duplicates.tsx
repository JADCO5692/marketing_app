import { useState } from "react"
import { useDuplicates, useMergeDuplicate, useDismissDuplicate } from "@/hooks/useApi"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { KPI_TIPS } from "@/lib/kpi-tips"
import { Merge, X, ChevronLeft, ChevronRight } from "lucide-react"

function ScoreRow({ label, a, b, tipKey }: { label: string; a: any; b: any; tipKey?: string }) {
  return (
    <tr className="border-b">
      <td className="py-1.5 pr-3 text-xs text-slate-400" title={tipKey ? KPI_TIPS[tipKey] : undefined}>{label}</td>
      <td className={`py-1.5 text-xs font-medium ${a == null ? "text-slate-300" : "text-slate-700"}`}>{a ?? "—"}</td>
      <td className={`py-1.5 pl-3 text-xs font-medium ${b == null ? "text-slate-300" : "text-slate-700"}`}>{b ?? "—"}</td>
    </tr>
  )
}

export function Duplicates() {
  const [page, setPage] = useState(1)
  const { data, isLoading } = useDuplicates({ page, limit: 10 })
  const merge = useMergeDuplicate()
  const dismiss = useDismissDuplicate()

  const pairs = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.ceil(total / 10)

  if (isLoading) return <div className="p-8 text-sm text-slate-400">Loading…</div>

  return (
    <div className="p-6 max-w-5xl">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">Duplicates</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          {total} pair{total !== 1 ? "s" : ""} pending review · Leads are auto-merged at ≥97% similarity
        </p>
      </div>

      {pairs.length === 0 && (
        <div className="rounded-xl border bg-white py-16 text-center text-sm text-slate-400">
          No duplicate pairs to review
        </div>
      )}

      <div className="space-y-4">
        {pairs.map((pair: any) => {
          const dup = pair.duplicate
          const orig = pair.original

          return (
            <div key={dup.id} className="rounded-xl border bg-white p-5">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <span className="rounded-full bg-amber-100 px-2 py-0.5 text-amber-700 font-medium">
                    {pair.similarity != null ? `${(pair.similarity * 100).toFixed(0)}% similar` : "Exact match"}
                  </span>
                  {pair.match_type && <span>· {pair.match_type}</span>}
                </div>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => dismiss.mutate(dup.id)}
                    disabled={dismiss.isPending}
                  >
                    <X size={13} /> Dismiss
                  </Button>
                  <Button
                    size="sm"
                    className="bg-brand-900 hover:bg-brand-900/90"
                    onClick={() => merge.mutate({ duplicateId: dup.id, keepId: orig.id })}
                    disabled={merge.isPending}
                  >
                    <Merge size={13} /> Merge into original
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-6">
                {[{ lead: orig, label: "Original" }, { lead: dup, label: "Duplicate" }].map(({ lead, label }) => (
                  <div key={lead.id}>
                    <p className="text-xs font-medium text-slate-400 mb-2 uppercase tracking-wide">{label}</p>
                    <p className="font-semibold text-slate-900 text-sm">{lead.first_name} {lead.last_name}</p>
                    <p className="text-xs text-slate-500 mb-3">{lead.email}</p>
                    <table className="w-full">
                      <tbody>
                        <ScoreRow label="Company" a={orig.company_name} b={dup.company_name} />
                        <ScoreRow label="Title" a={orig.title} b={dup.title} />
                        <ScoreRow label="Phone" a={orig.phone} b={dup.phone} />
                        <ScoreRow label="ICP score" a={orig.icp_score} b={dup.icp_score} tipKey="icp_score" />
                        <ScoreRow label="Intent" a={orig.intent_score} b={dup.intent_score} tipKey="intent_score" />
                        <ScoreRow label="Status" a={orig.status} b={dup.status} />
                      </tbody>
                    </table>
                  </div>
                ))}
              </div>
            </div>
          )
        })}
      </div>

      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-between text-sm text-slate-500">
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
