import { useState } from "react"
import { useCompanies } from "@/hooks/useApi"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { KPI_TIPS } from "@/lib/kpi-tips"
import { scoreColorClass } from "@/lib/utils"
import { Search, ChevronLeft, ChevronRight, ExternalLink } from "lucide-react"

const SIZE_OPTIONS = ["", "1-10", "11-50", "51-200", "201-500", "501-1000", "1001-5000", "5000+"]

export function Companies() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")
  const [size, setSize] = useState("")
  const [selected, setSelected] = useState<any | null>(null)

  const { data, isLoading } = useCompanies({
    page,
    limit: 20,
    search: search || undefined,
    company_size: size || undefined,
  })

  const companies = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.ceil(total / 20)

  return (
    <div className="flex h-full">
      <div className="flex-1 p-6 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-semibold text-slate-900">
            Companies <span className="text-sm font-normal text-slate-400">({total})</span>
          </h1>
        </div>

        <div className="flex gap-3 mb-4">
          <div className="relative flex-1 max-w-sm">
            <Search size={14} className="absolute left-2.5 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search company name, industry…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1) }}
              className="w-full rounded-lg border py-2 pl-8 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
            />
          </div>
          <select
            value={size}
            onChange={(e) => { setSize(e.target.value); setPage(1) }}
            className="rounded-lg border px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-900"
          >
            {SIZE_OPTIONS.map((s) => (
              <option key={s} value={s}>{s || "All sizes"}</option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {isLoading && (
            <p className="col-span-3 py-12 text-center text-sm text-slate-400">Loading…</p>
          )}
          {!isLoading && companies.length === 0 && (
            <p className="col-span-3 py-12 text-center text-sm text-slate-400">No companies found</p>
          )}
          {companies.map((co: any) => (
            <div
              key={co.id}
              onClick={() => setSelected(co.id === selected?.id ? null : co)}
              className={`rounded-xl border bg-white p-4 cursor-pointer transition-shadow hover:shadow-md ${
                selected?.id === co.id ? "ring-2 ring-brand-900" : ""
              }`}
            >
              <div className="flex items-start justify-between gap-2 mb-2">
                <div>
                  <h3 className="font-semibold text-slate-900 text-sm">{co.name}</h3>
                  <p className="text-xs text-slate-400">{co.industry ?? "—"} · {co.company_size ?? "?"} employees</p>
                </div>
                {co.website && (
                  <a
                    href={co.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-slate-400 hover:text-brand-900 shrink-0"
                  >
                    <ExternalLink size={13} />
                  </a>
                )}
              </div>

              <div className="flex gap-3 text-xs text-center mt-3">
                {[
                  { key: "hiring_velocity", label: "Hiring", tip: KPI_TIPS.hiring_velocity },
                  { key: "website_quality_score", label: "Web", tip: KPI_TIPS.website_quality_score },
                  { key: "lead_count", label: "Leads", tip: KPI_TIPS.lead_count },
                ].map(({ key, label, tip }) => (
                  <div key={key} className="flex-1 rounded-lg bg-slate-50 py-1.5" title={tip}>
                    <div className={`font-bold ${scoreColorClass(co[key])}`}>{co[key] ?? "—"}</div>
                    <div className="text-slate-400">{label}</div>
                  </div>
                ))}
              </div>

              {co.pain_points?.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-1">
                  {co.pain_points.slice(0, 3).map((p: string) => (
                    <span key={p} className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600">{p}</span>
                  ))}
                </div>
              )}
            </div>
          ))}
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

      {/* Detail panel */}
      {selected && (
        <div className="w-80 border-l bg-white overflow-y-auto p-5 shrink-0">
          <h2 className="font-semibold text-slate-900 mb-1">{selected.name}</h2>
          <p className="text-xs text-slate-500 mb-4">{selected.industry} · {selected.funding_stage ?? "Unknown funding"}</p>

          <div className="space-y-3 text-sm">
            {[
              { label: "HQ Location", value: selected.hq_location },
              { label: "Founded", value: selected.founded_year },
              { label: "Employee count", value: selected.employee_count },
              { label: "Revenue range", value: selected.revenue_range },
              { label: "Research status", value: selected.research_status },
            ].map(({ label, value }) =>
              value ? (
                <div key={label}>
                  <span className="text-xs text-slate-400">{label}</span>
                  <p className="text-slate-700">{value}</p>
                </div>
              ) : null
            )}

            {selected.tech_stack?.length > 0 && (
              <div>
                <span className="text-xs text-slate-400">Tech stack</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {selected.tech_stack.map((t: string) => (
                    <span key={t} className="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700">{t}</span>
                  ))}
                </div>
              </div>
            )}

            {selected.recent_news?.length > 0 && (
              <div>
                <span className="text-xs text-slate-400">Recent news</span>
                <ul className="mt-1 space-y-1">
                  {selected.recent_news.slice(0, 3).map((n: any, i: number) => (
                    <li key={i} className="text-xs text-slate-600">{n.title ?? n}</li>
                  ))}
                </ul>
              </div>
            )}

            {selected.value_proposition && (
              <div>
                <span className="text-xs text-slate-400">Value proposition</span>
                <p className="text-xs text-slate-600 mt-0.5">{selected.value_proposition}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
