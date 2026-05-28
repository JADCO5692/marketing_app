import { useState, useRef, useEffect } from "react"
import {
  useLeads, useResearchLead, useDeleteLead,
  useCreateLead, useDeleteAllLeads,
} from "@/hooks/useApi"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { KPI_TIPS } from "@/lib/kpi-tips"
import { formatScore, scoreColorClass, downloadBlob } from "@/lib/utils"
import {
  Search, Download, FlaskConical, Trash2, ChevronLeft, ChevronRight,
  Plus, AlertTriangle, Columns3, X,
} from "lucide-react"
import { leadsApi } from "@/lib/api"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import api from "@/lib/api"

const STATUS_OPTIONS = ["", "raw", "researching", "enriched", "duplicate", "merged", "invalid"]

// All columns available from the leads table
const ALL_COLUMNS: { key: string; label: string; default?: boolean }[] = [
  { key: "name", label: "Name", default: true },
  { key: "email", label: "Email" },
  { key: "phone", label: "Phone" },
  { key: "linkedin_url", label: "LinkedIn" },
  { key: "company_name", label: "Company", default: true },
  { key: "job_title", label: "Title", default: true },
  { key: "department", label: "Department" },
  { key: "seniority_level", label: "Seniority" },
  { key: "is_decision_maker", label: "Decision Maker" },
  { key: "budget_authority", label: "Budget Auth." },
  { key: "status", label: "Status", default: true },
  { key: "icp_score", label: "ICP", default: true },
  { key: "intent_score", label: "Intent", default: true },
  { key: "engagement_readiness", label: "Engage", default: true },
  { key: "campaign_type_match", label: "Campaign Fit" },
  { key: "email_verified", label: "Email Verified" },
  { key: "email_deliverability", label: "Deliverability" },
  { key: "email_type", label: "Email Type" },
  { key: "source_file", label: "Source File" },
  { key: "created_at", label: "Created At" },
]

function KpiCell({ value, tipKey }: { value: number | null; tipKey: string }) {
  if (value == null) return <span className="text-slate-300">—</span>
  return (
    <span title={KPI_TIPS[tipKey]} className={`font-medium ${scoreColorClass(value)}`}>
      {formatScore(value)}
    </span>
  )
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    year: "numeric", month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  })
}

function renderCell(lead: any, key: string) {
  const v = lead[key]
  if (v == null || v === "") return <span className="text-slate-300">—</span>
  if (["icp_score", "intent_score", "engagement_readiness"].includes(key)) {
    return <KpiCell value={v} tipKey={key} />
  }
  if (key === "status") return <Badge variant={v as any}>{v}</Badge>
  if (typeof v === "boolean") return v ? "Yes" : "No"
  if (key === "created_at") return <span className="whitespace-nowrap text-xs">{formatDateTime(v)}</span>
  if (key === "linkedin_url") {
    return <a href={v} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()} className="text-brand-900 underline text-xs">Link</a>
  }
  if (key === "name") {
    return (
      <>
        <span className="font-medium text-slate-900">{v}</span>
        {lead.email && <div className="text-xs text-slate-400">{lead.email}</div>}
      </>
    )
  }
  return String(v)
}

// ── Drawer Section ─────────────────────────────────────────────────────────────
function DrawerSection({
  title,
  fields,
  children,
}: {
  title: string
  fields: { label: string; value: string | null | undefined; link?: boolean }[]
  children?: React.ReactNode
}) {
  const nonEmpty = fields.filter((f) => f.value != null && f.value !== "")
  if (nonEmpty.length === 0 && !children) return null
  return (
    <div>
      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">{title}</p>
      <div className="space-y-2">
        {nonEmpty.map(({ label, value, link }) => (
          <div key={label}>
            <span className="text-xs text-slate-400">{label}</span>
            {link
              ? <a href={value!} target="_blank" rel="noreferrer" className="block text-brand-900 underline text-xs truncate">{value}</a>
              : <p className="text-slate-700 break-all text-xs mt-0.5">{value}</p>
            }
          </div>
        ))}
        {children}
      </div>
    </div>
  )
}

// ── Column Picker ─────────────────────────────────────────────────────────────
function ColumnPicker({
  visible, onChange,
}: { visible: Set<string>; onChange: (v: Set<string>) => void }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener("mousedown", handler)
    return () => document.removeEventListener("mousedown", handler)
  }, [])

  function toggle(key: string) {
    const next = new Set(visible)
    next.has(key) ? next.delete(key) : next.add(key)
    onChange(next)
  }

  return (
    <div ref={ref} className="relative">
      <Button size="sm" variant="outline" onClick={() => setOpen((o) => !o)}>
        <Columns3 size={14} /> Columns
      </Button>
      {open && (
        <div className="absolute right-0 top-9 z-30 w-52 rounded-xl border bg-white shadow-lg p-2">
          <p className="text-xs font-medium text-slate-500 px-2 pb-1">Show / hide columns</p>
          {ALL_COLUMNS.map((col) => (
            <label key={col.key} className="flex items-center gap-2 px-2 py-1 rounded hover:bg-slate-50 cursor-pointer text-sm text-slate-700">
              <input
                type="checkbox"
                checked={visible.has(col.key)}
                onChange={() => toggle(col.key)}
                className="accent-brand-900"
              />
              {col.label}
            </label>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Add Lead Modal ────────────────────────────────────────────────────────────
function AddLeadModal({ onClose }: { onClose: () => void }) {
  const createLead = useCreateLead()
  const [form, setForm] = useState({
    name: "", email: "", phone: "", job_title: "", company_name: "", linkedin_url: "",
  })

  const field = (key: keyof typeof form) => (
    <div>
      <label className="block text-xs font-medium text-slate-500 mb-1 capitalize">
        {key.replace("_", " ")}
      </label>
      <input
        type="text"
        value={form[key]}
        onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
        placeholder={key === "email" ? "name@company.com" : key === "linkedin_url" ? "https://linkedin.com/in/..." : ""}
        className="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
      />
    </div>
  )

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const payload = Object.fromEntries(
      Object.entries(form).filter(([, v]) => v.trim() !== "")
    )
    await createLead.mutateAsync(payload)
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-base font-semibold text-slate-900">Add Lead</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-lg leading-none">×</button>
        </div>
        <form onSubmit={handleSubmit} className="px-6 py-5 space-y-3">
          {field("name")}
          {field("email")}
          {field("phone")}
          {field("job_title")}
          {field("company_name")}
          {field("linkedin_url")}
          <p className="text-xs text-slate-400 pt-1">
            At least one field required. Run Research after adding to enrich the lead.
          </p>
          <div className="flex gap-2 pt-2">
            <Button
              type="submit"
              className="flex-1 bg-brand-900 hover:bg-brand-900/90"
              disabled={createLead.isPending || Object.values(form).every((v) => !v.trim())}
            >
              {createLead.isPending ? "Adding…" : "Add Lead"}
            </Button>
            <Button type="button" variant="outline" onClick={onClose}>Cancel</Button>
          </div>
        </form>
      </div>
    </div>
  )
}

// ── Delete All Confirmation Modal ─────────────────────────────────────────────
function DeleteAllModal({ total, onClose }: { total: number; onClose: () => void }) {
  const deleteAll = useDeleteAllLeads()
  const [confirm, setConfirm] = useState("")

  async function handleDelete() {
    await deleteAll.mutateAsync()
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4">
        <div className="px-6 py-5">
          <div className="flex items-start gap-3 mb-4">
            <div className="rounded-full bg-danger-100 p-2 shrink-0">
              <AlertTriangle size={16} className="text-danger-700" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-slate-900">Delete all leads?</h2>
              <p className="text-sm text-slate-500 mt-0.5">
                This will permanently delete all <strong>{total}</strong> leads and their research logs. This cannot be undone.
              </p>
            </div>
          </div>
          <label className="block text-xs font-medium text-slate-500 mb-1">
            Type <span className="font-mono text-danger-700">DELETE</span> to confirm
          </label>
          <input
            type="text"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            autoFocus
            className="w-full rounded-lg border border-danger-700/30 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-danger-700 mb-4"
            placeholder="DELETE"
          />
          <div className="flex gap-2">
            <Button
              className="flex-1 bg-danger-700 hover:bg-danger-700/90 text-white"
              disabled={confirm !== "DELETE" || deleteAll.isPending}
              onClick={handleDelete}
            >
              {deleteAll.isPending ? "Deleting…" : "Delete All"}
            </Button>
            <Button variant="outline" onClick={onClose}>Cancel</Button>
          </div>
        </div>
      </div>
    </div>
  )
}

// ── Delete Selected Confirmation Modal ────────────────────────────────────────
function DeleteSelectedModal({
  count, onClose, onConfirm, isPending,
}: { count: number; onClose: () => void; onConfirm: () => void; isPending: boolean }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 px-6 py-5">
        <div className="flex items-start gap-3 mb-5">
          <div className="rounded-full bg-danger-100 p-2 shrink-0">
            <AlertTriangle size={16} className="text-danger-700" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-slate-900">Delete {count} lead{count !== 1 ? "s" : ""}?</h2>
            <p className="text-sm text-slate-500 mt-0.5">This cannot be undone.</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            className="flex-1 bg-danger-700 hover:bg-danger-700/90 text-white"
            disabled={isPending}
            onClick={onConfirm}
          >
            {isPending ? "Deleting…" : `Delete ${count}`}
          </Button>
          <Button variant="outline" onClick={onClose}>Cancel</Button>
        </div>
      </div>
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────
export function Leads() {
  const [page, setPage] = useState(1)
  const [limit, setLimit] = useState<number>(() => {
    const saved = localStorage.getItem("leads:pageSize")
    return saved ? Number(saved) : 25
  })
  const [search, setSearch] = useState("")
  const [status, setStatus] = useState("")
  const [selected, setSelected] = useState<string | null>(null)
  const [showAdd, setShowAdd] = useState(false)
  const [showDeleteAll, setShowDeleteAll] = useState(false)
  const [showDeleteSelected, setShowDeleteSelected] = useState(false)
  const [checked, setChecked] = useState<Set<string>>(new Set())
  const [visibleCols, setVisibleCols] = useState<Set<string>>(() => {
    try {
      const saved = localStorage.getItem("leads:visibleCols")
      if (saved) return new Set(JSON.parse(saved))
    } catch {}
    return new Set(ALL_COLUMNS.filter((c) => c.default).map((c) => c.key))
  })

  const { data, isLoading } = useLeads({ page, limit, search: search || undefined, status: status || undefined })
  const researchLead = useResearchLead()
  const deleteLead = useDeleteLead()
  const qc = useQueryClient()
  const deleteSelected = useMutation({
    mutationFn: (ids: string[]) =>
      Promise.all(ids.map((id) => api.delete(`/leads/${id}`))),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["leads"] })
      toast.success(`Deleted ${checked.size} lead${checked.size !== 1 ? "s" : ""}`)
      setChecked(new Set())
      setShowDeleteSelected(false)
    },
    onError: () => toast.error("Failed to delete selected leads"),
  })

  const leads = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.ceil(total / limit)
  const selectedLead = leads.find((l: any) => l.id === selected)
  const allChecked = leads.length > 0 && leads.every((l: any) => checked.has(l.id))

  function toggleCheck(id: string, e: React.MouseEvent) {
    e.stopPropagation()
    setChecked((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  function toggleAll(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.checked) {
      setChecked((prev) => {
        const next = new Set(prev)
        leads.forEach((l: any) => next.add(l.id))
        return next
      })
    } else {
      setChecked((prev) => {
        const next = new Set(prev)
        leads.forEach((l: any) => next.delete(l.id))
        return next
      })
    }
  }

  async function handleExport() {
    const params: Record<string, string> = {}
    if (search) params.search = search
    if (status) params.status = status
    const res = await leadsApi.exportCsv(params)
    downloadBlob(new Blob([res.data]), "leads.csv")
  }

  const visibleColDefs = ALL_COLUMNS.filter((c) => visibleCols.has(c.key))
  const colCount = visibleColDefs.length + 2 // +checkbox +actions

  return (
    <div className="flex h-full">
      {showAdd && <AddLeadModal onClose={() => setShowAdd(false)} />}
      {showDeleteAll && (
        <DeleteAllModal total={total} onClose={() => { setShowDeleteAll(false); setSelected(null) }} />
      )}
      {showDeleteSelected && (
        <DeleteSelectedModal
          count={checked.size}
          isPending={deleteSelected.isPending}
          onClose={() => setShowDeleteSelected(false)}
          onConfirm={() => deleteSelected.mutate(Array.from(checked))}
        />
      )}

      {/* Main table area */}
      <div className="flex-1 p-6 overflow-auto">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-xl font-semibold text-slate-900">
            Leads <span className="text-sm font-normal text-slate-400">({total})</span>
          </h1>
          <div className="flex items-center gap-2">
            {checked.size > 0 && (
              <Button
                size="sm"
                variant="outline"
                className="text-danger-700 border-danger-700/30 hover:bg-danger-100"
                onClick={() => setShowDeleteSelected(true)}
              >
                <Trash2 size={14} /> Delete {checked.size} selected
              </Button>
            )}
            <ColumnPicker
              visible={visibleCols}
              onChange={(v) => {
                setVisibleCols(v)
                localStorage.setItem("leads:visibleCols", JSON.stringify(Array.from(v)))
              }}
            />
            <Button size="sm" variant="outline" onClick={handleExport}>
              <Download size={14} /> Export CSV
            </Button>
            <Button size="sm" className="bg-brand-900 hover:bg-brand-900/90" onClick={() => setShowAdd(true)}>
              <Plus size={14} /> Add Lead
            </Button>
            {total > 0 && (
              <Button
                size="sm"
                variant="outline"
                className="text-danger-700 border-danger-700/30 hover:bg-danger-100"
                onClick={() => setShowDeleteAll(true)}
              >
                <Trash2 size={14} /> Delete All
              </Button>
            )}
          </div>
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
        <div className="rounded-xl border bg-white overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b bg-slate-50 text-xs font-medium text-slate-500">
                <th className="px-4 py-3 w-8">
                  <input
                    type="checkbox"
                    checked={allChecked}
                    onChange={toggleAll}
                    className="accent-brand-900"
                  />
                </th>
                {visibleColDefs.map((col) => (
                  <th
                    key={col.key}
                    className={`px-4 py-3 text-left ${["icp_score", "intent_score", "engagement_readiness"].includes(col.key) ? "text-right" : ""}`}
                    title={KPI_TIPS[col.key]}
                  >
                    {col.label}
                  </th>
                ))}
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {isLoading && (
                <tr><td colSpan={colCount} className="py-12 text-center text-sm text-slate-400">Loading…</td></tr>
              )}
              {!isLoading && leads.length === 0 && (
                <tr>
                  <td colSpan={colCount} className="py-12 text-center text-sm text-slate-400">
                    No leads found.{" "}
                    <button onClick={() => setShowAdd(true)} className="text-brand-900 underline">Add one manually</button>
                    {" "}or upload a CSV.
                  </td>
                </tr>
              )}
              {leads.map((lead: any) => (
                <tr
                  key={lead.id}
                  onClick={() => setSelected(lead.id === selected ? null : lead.id)}
                  className={`border-b cursor-pointer transition-colors hover:bg-slate-50 ${selected === lead.id ? "bg-brand-900/5" : ""}`}
                >
                  <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={checked.has(lead.id)}
                      onChange={(e) => { e.stopPropagation(); toggleCheck(lead.id, e as any) }}
                      onClick={(e) => e.stopPropagation()}
                      className="accent-brand-900"
                    />
                  </td>
                  {visibleColDefs.map((col) => (
                    <td
                      key={col.key}
                      className={`px-4 py-3 text-slate-700 ${["icp_score", "intent_score", "engagement_readiness"].includes(col.key) ? "text-right" : ""}`}
                    >
                      {renderCell(lead, col.key)}
                    </td>
                  ))}
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-1">
                      <button
                        title="Run Research"
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
        <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
          <div className="flex items-center gap-2">
            <span>Rows per page:</span>
            <select
              value={limit}
              onChange={(e) => {
                const v = Number(e.target.value)
                setLimit(v)
                localStorage.setItem("leads:pageSize", String(v))
                setPage(1)
              }}
              className="rounded-lg border px-2 py-1 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-900"
            >
              {[10, 25, 50, 100, 200].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
            <span className="text-slate-400">· {total} total</span>
          </div>
          {totalPages > 1 && (
            <div className="flex items-center gap-2">
              <span>Page {page} of {totalPages}</span>
              <Button size="sm" variant="outline" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                <ChevronLeft size={14} />
              </Button>
              <Button size="sm" variant="outline" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                <ChevronRight size={14} />
              </Button>
            </div>
          )}
        </div>
      </div>

      {/* Detail drawer */}
      {selectedLead && (
        <div className="w-80 border-l bg-white overflow-y-auto shrink-0 flex flex-col">
          {/* Sticky header */}
          <div className="sticky top-0 z-10 bg-white border-b px-5 py-4">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <h2 className="font-semibold text-slate-900 truncate">
                  {selectedLead.name || selectedLead.email || "—"}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5 truncate">
                  {[selectedLead.job_title, selectedLead.company_name || selectedLead.raw_csv_data?.company_name].filter(Boolean).join(" @ ")}
                </p>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="shrink-0 rounded p-1 text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X size={15} />
              </button>
            </div>
            <div className="mt-2">
              <Badge variant={selectedLead.status as any}>{selectedLead.status}</Badge>
            </div>
          </div>

          {/* Scrollable body */}
          <div className="flex-1 overflow-y-auto p-5 space-y-5 text-sm">

            {/* Score cards */}
            <div className="grid grid-cols-3 gap-2 text-center">
              {[
                { key: "icp_score", label: "ICP" },
                { key: "intent_score", label: "Intent" },
                { key: "engagement_readiness", label: "Engage" },
              ].map(({ key, label }) => (
                <div key={key} className="rounded-lg bg-slate-50 p-2" title={KPI_TIPS[key]}>
                  <div className={`text-lg font-bold ${scoreColorClass(selectedLead[key])}`}>
                    {selectedLead[key] != null ? formatScore(selectedLead[key]) : "—"}
                  </div>
                  <div className="text-xs text-slate-400">{label}</div>
                </div>
              ))}
            </div>

            {/* Contact */}
            <DrawerSection title="Contact" fields={[
              { label: "Email", value: selectedLead.email },
              { label: "Phone", value: selectedLead.phone },
              { label: "LinkedIn", value: selectedLead.linkedin_url, link: true },
              { label: "Email verified", value: selectedLead.email_verified != null ? (selectedLead.email_verified ? "Yes" : "No") : null },
              { label: "Deliverability", value: selectedLead.email_deliverability },
              { label: "Email type", value: selectedLead.email_type },
            ]} />

            {/* Role */}
            <DrawerSection title="Role" fields={[
              { label: "Title", value: selectedLead.job_title },
              { label: "Department", value: selectedLead.department },
              { label: "Seniority", value: selectedLead.seniority_level },
              { label: "Decision maker", value: selectedLead.is_decision_maker != null ? (selectedLead.is_decision_maker ? "Yes" : "No") : null },
              { label: "Budget authority", value: selectedLead.budget_authority != null ? (selectedLead.budget_authority ? "Yes" : "No") : null },
            ]} />

            {/* AI Insights */}
            <DrawerSection title="AI Insights" fields={[
              { label: "Campaign fit", value: selectedLead.campaign_type_match },
            ]}>
              {selectedLead.personalization_tags?.length > 0 && (
                <div>
                  <span className="text-xs text-slate-400">Personalization tags</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {selectedLead.personalization_tags.map((t: string) => (
                      <span key={t} className="rounded-full bg-brand-900/10 text-brand-900 px-2 py-0.5 text-xs">{t}</span>
                    ))}
                  </div>
                </div>
              )}
              {selectedLead.pain_point_clusters?.length > 0 && (
                <div>
                  <span className="text-xs text-slate-400">Pain points</span>
                  <ul className="mt-1 space-y-0.5">
                    {selectedLead.pain_point_clusters.map((p: string) => (
                      <li key={p} className="text-xs text-slate-600 before:content-['·'] before:mr-1.5 before:text-slate-400">{p}</li>
                    ))}
                  </ul>
                </div>
              )}
              {selectedLead.competitive_intel && Object.keys(selectedLead.competitive_intel).length > 0 && (
                <div>
                  <span className="text-xs text-slate-400">Competitive intel</span>
                  <pre className="mt-1 text-xs text-slate-600 whitespace-pre-wrap bg-slate-50 rounded p-2 max-h-32 overflow-y-auto">
                    {JSON.stringify(selectedLead.competitive_intel, null, 2)}
                  </pre>
                </div>
              )}
            </DrawerSection>

            {/* Meta */}
            <DrawerSection title="Meta" fields={[
              { label: "Source file", value: selectedLead.source_file },
              { label: "Source row", value: selectedLead.source_row != null ? String(selectedLead.source_row) : null },
              { label: "Created", value: selectedLead.created_at ? formatDateTime(selectedLead.created_at) : null },
              { label: "Updated", value: selectedLead.updated_at ? formatDateTime(selectedLead.updated_at) : null },
            ]} />
          </div>

          {/* Sticky footer */}
          <div className="sticky bottom-0 bg-white border-t px-5 py-3">
            <Button
              size="sm"
              className="w-full bg-brand-900 hover:bg-brand-900/90"
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
