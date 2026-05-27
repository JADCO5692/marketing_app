import { useState } from "react"
import { useLeads, useResearchLead, useDeleteLead, useUpdateLead } from "@/hooks/useApi"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { KPI_TIPS } from "@/lib/kpi-tips"
import { formatScore, scoreColorClass, downloadBlob } from "@/lib/utils"
import { Search, Download, FlaskConical, Trash2, ChevronLeft, ChevronRight } from "lucide-react"
import { leadsApi } from "@/lib/api"

const STATUS_OPTIONS = ["", "raw", "researching", "enriched", "duplicate", "merged", "invalid"]

function KpiCell({ label, value, tipKey }: { label: string; value: number | null; tipKey: string }) {
  if (value == null) return <span className="text-slate-300">—</span>
  return (
    <span
      title={KPI_TIPS[tipKey]}
      className={`font-medium ${scoreColorClass(value)}`}
    >
      {formatScore(value)}
    </span>
  )
}

export function Leads() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [status, setStatus] = useState("")
  const [selected, setSelected] = useState<string | null>(null)

  const { data, isLoading } = useLeads({ page, limit: 25, search: search || undefined, status: status || undefined })
  const researchLead = useResearchLead()
  const deleteLead = useDeleteLead()
  const updateLead = useUpdateLead()

  const leads = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.ceil(total / 25)

  const selectedLead = leads.find((l: any) => l.id === selected)

  async function handleExport() {
    const params: Record<string, string> = {}
    if (search) params.search = search
    if (status) params.status = status
    const res = await leadsApi.exportCsv(params)
    downloadBlob(new Blob([res.data]), "leads.csv")
  }

  return (
    <div className="flex h-full">
      {/* Main table area */}
      <div className="flex-1 p-6 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-semibold text-slate-900">Leads <span className="text-sm font-normal text-slate-400">({total})</span></h1>
          <Button size="sm" variant="outline" onClick={handleExport}>
            <Download size={14} /> Export CSV
          </Button>
        </div>

        {/* Filters */}
        <div className="flex gap-3 mb-4">
          <div className="relative flex-1 max-w-sm">
            <Search size={14} className="absolute left-2.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search name, email, company…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1) }}
              className="w-full rounded-lg border py-2 pl-8 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
            />
          </div>
          <select
            value={status}
            onChange={(e) => { setStatus(e.target.value); setPage(1) }}
            className="rounded-lg border px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-900"
          >
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s || "All statuses"}</option>
            ))}
          </select>
        </div>

        {/* Table */}
        <div className="rounded-xl border bg-white overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-slate-50 text-xs font-medium text-slate-500">
                <th className="px-4 py-3 text-left">Name</th>
                <th className="px-4 py-3 text-left">Company</th>
                <th className="px-4 py-3 text-left">Title</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-right" title={KPI_TIPS.icp_score}>ICP</th>
                <th className="px-4 py-3 text-right" title={KPI_TIPS.intent_score}>Intent</th>
                <th className="px-4 py-3 text-right" title={KPI_TIPS.engagement_readiness}>Engage</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr><td colSpan={8} className="py-12 text-center text-sm text-slate-400">Loading…</td></tr>
              )}
              {!isLoading && leads.length === 0 && (
                <tr><td colSpan={8} className="py-12 text-center text-sm text-slate-400">No leads found</td></tr>
              )}
              {leads.map((lead: any) => (
                <tr
                  key={lead.id}
                  onClick={() => setSelected(lead.id === selected ? null : lead.id)}
                  className={`border-b cursor-pointer transition-colors hover:bg-slate-50 ${selected === lead.id ? "bg-brand-900/5" : ""}`}
                >
                  <td className="px-4 py-3 font-medium text-slate-900">
                    {lead.first_name} {lead.last_name}
                    {lead.email && <div className="text-xs text-slate-400">{lead.email}</div>}
                  </td>
                  <td className="px-4 py-3 text-slate-600">{lead.company_name ?? "—"}</td>
                  <td className="px-4 py-3 text-slate-600">{lead.title ?? "—"}</td>
                  <td className="px-4 py-3">
                    <Badge variant={lead.status as any}>{lead.status}</Badge>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <KpiCell label="ICP" value={lead.icp_score} tipKey="icp_score" />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <KpiCell label="Intent" value={lead.intent_score} tipKey="intent_score" />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <KpiCell label="Engage" value={lead.engagement_readiness} tipKey="engagement_readiness" />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        title="Research"
                        onClick={(e) => { e.stopPropagation(); researchLead.mutate(lead.id) }}
                        className="rounded p-1 hover:bg-slate-100 text-slate-400 hover:text-brand-900"
                      >
                        <FlaskConical size={14} />
                      </button>
                      <button
                        title="Delete"
                        onClick={(e) => { e.stopPropagation(); deleteLead.mutate(lead.id) }}
                        className="rounded p-1 hover:bg-slate-100 text-slate-400 hover:text-danger-700"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
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

      {/* Detail drawer */}
      {selectedLead && (
        <div className="w-80 border-l bg-white overflow-y-auto p-5 shrink-0">
          <div className="mb-4">
            <h2 className="font-semibold text-slate-900">{selectedLead.first_name} {selectedLead.last_name}</h2>
            <p className="text-xs text-slate-500">{selectedLead.title} @ {selectedLead.company_name}</p>
          </div>

          <div className="space-y-3 text-sm">
            {[
              { label: "Email", value: selectedLead.email },
              { label: "Phone", value: selectedLead.phone },
              { label: "Industry", value: selectedLead.industry },
              { label: "Region", value: selectedLead.region },
              { label: "Seniority", value: selectedLead.seniority_level, tip: KPI_TIPS.seniority_level },
              { label: "Campaign fit", value: selectedLead.campaign_type_match, tip: KPI_TIPS.campaign_type_match },
            ].map(({ label, value, tip }) =>
              value ? (
                <div key={label}>
                  <span title={tip} className="text-xs text-slate-400">{label}</span>
                  <p className="text-slate-700">{value}</p>
                </div>
              ) : null
            )}

            <div className="pt-2 grid grid-cols-3 gap-2 text-center">
              {[
                { key: "icp_score", label: "ICP" },
                { key: "intent_score", label: "Intent" },
                { key: "engagement_readiness", label: "Engage" },
              ].map(({ key, label }) => (
                <div key={key} className="rounded-lg bg-slate-50 p-2" title={KPI_TIPS[key]}>
                  <div className={`text-lg font-bold ${scoreColorClass(selectedLead[key])}`}>
                    {selectedLead[key] ?? "—"}
                  </div>
                  <div className="text-xs text-slate-400">{label}</div>
                </div>
              ))}
            </div>

            {selectedLead.personalization_tags?.length > 0 && (
              <div>
                <span className="text-xs text-slate-400">Tags</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {selectedLead.personalization_tags.map((t: string) => (
                    <span key={t} className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{t}</span>
                  ))}
                </div>
              </div>
            )}

            {selectedLead.pain_point_clusters?.length > 0 && (
              <div>
                <span className="text-xs text-slate-400">Pain points</span>
                <ul className="mt-1 text-xs text-slate-600 space-y-0.5">
                  {selectedLead.pain_point_clusters.map((p: string) => (
                    <li key={p} className="before:content-['•'] before:mr-1">{p}</li>
                  ))}
                </ul>
              </div>
            )}

            <Button
              size="sm"
              className="w-full mt-2 bg-brand-900 hover:bg-brand-900/90"
              onClick={() => researchLead.mutate(selectedLead.id)}
              disabled={selectedLead.status === "researching"}
            >
              <FlaskConical size={14} />
              {selectedLead.status === "researching" ? "Researching…" : "Run Research"}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
