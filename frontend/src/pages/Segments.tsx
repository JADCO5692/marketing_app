import { useState } from "react"
import { useSegments, useCreateSegment, useDeleteSegment, useSegmentPreview } from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import { KPI_TIPS } from "@/lib/kpi-tips"
import { Plus, Trash2, Download, Eye } from "lucide-react"
import { segmentsApi } from "@/lib/api"
import { downloadBlob } from "@/lib/utils"

const FILTER_FIELDS = [
  { key: "icp_score", label: "ICP Score", type: "range", tip: KPI_TIPS.icp_score },
  { key: "intent_score", label: "Intent Score", type: "range", tip: KPI_TIPS.intent_score },
  { key: "engagement_readiness", label: "Engagement Readiness", type: "range", tip: KPI_TIPS.engagement_readiness },
  { key: "industry", label: "Industry", type: "text" },
  { key: "region", label: "Region", type: "text" },
  { key: "company_size", label: "Company Size", type: "text" },
  { key: "funding_stage", label: "Funding Stage", type: "text", tip: KPI_TIPS.funding_stage },
  { key: "seniority_level", label: "Seniority", type: "text", tip: KPI_TIPS.seniority_level },
  { key: "is_decision_maker", label: "Decision Maker", type: "bool", tip: KPI_TIPS.is_decision_maker },
  { key: "email_verified", label: "Email Verified", type: "bool", tip: KPI_TIPS.email_verified },
  { key: "status", label: "Status", type: "text" },
]

interface FilterRule { field: string; op: string; value: string }

function FilterRow({
  rule,
  onUpdate,
  onRemove,
}: {
  rule: FilterRule
  onUpdate: (r: FilterRule) => void
  onRemove: () => void
}) {
  const fieldDef = FILTER_FIELDS.find((f) => f.key === rule.field)

  return (
    <div className="flex items-center gap-2 text-sm">
      <select
        value={rule.field}
        onChange={(e) => onUpdate({ ...rule, field: e.target.value, op: ">=", value: "" })}
        className="rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
      >
        {FILTER_FIELDS.map((f) => (
          <option key={f.key} value={f.key}>{f.label}</option>
        ))}
      </select>

      {fieldDef?.type === "bool" ? (
        <select
          value={rule.value}
          onChange={(e) => onUpdate({ ...rule, value: e.target.value })}
          className="rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
        >
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      ) : fieldDef?.type === "range" ? (
        <>
          <select
            value={rule.op}
            onChange={(e) => onUpdate({ ...rule, op: e.target.value })}
            className="rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
          >
            <option value=">=">≥</option>
            <option value="<=">≤</option>
            <option value="=">=</option>
          </select>
          <input
            type="number"
            min={0}
            max={100}
            value={rule.value}
            onChange={(e) => onUpdate({ ...rule, value: e.target.value })}
            className="w-20 rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
            placeholder="0–100"
          />
        </>
      ) : (
        <input
          type="text"
          value={rule.value}
          onChange={(e) => onUpdate({ ...rule, value: e.target.value })}
          className="flex-1 rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
          placeholder="value"
        />
      )}

      <button onClick={onRemove} className="text-slate-400 hover:text-danger-700">
        <Trash2 size={13} />
      </button>
    </div>
  )
}

function rulestoFilterRules(rules: FilterRule[]) {
  const out: Record<string, unknown> = {}
  for (const r of rules) {
    if (!r.value) continue
    const val = r.op === ">=" || r.op === "<=" || r.op === "="
      ? { [r.op]: Number(r.value) }
      : r.value === "true" ? true : r.value === "false" ? false : r.value
    out[r.field] = val
  }
  return out
}

export function Segments() {
  const { data: segments, isLoading } = useSegments()
  const createSegment = useCreateSegment()
  const deleteSegment = useDeleteSegment()

  const [creating, setCreating] = useState(false)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [rules, setRules] = useState<FilterRule[]>([
    { field: "icp_score", op: ">=", value: "70" },
  ])
  const [previewEnabled, setPreviewEnabled] = useState(false)

  const filterRules = rulestoFilterRules(rules)
  const { data: preview } = useSegmentPreview(filterRules, previewEnabled && creating)

  function addRule() {
    setRules((r) => [...r, { field: "icp_score", op: ">=", value: "" }])
  }

  function handleCreate() {
    if (!name.trim()) return
    createSegment.mutate(
      { name, description, filter_rules: filterRules },
      { onSuccess: () => { setCreating(false); setName(""); setDescription(""); setRules([]) } }
    )
  }

  return (
    <div className="p-6 max-w-4xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-slate-900">Segments</h1>
        {!creating && (
          <Button size="sm" className="bg-brand-900 hover:bg-brand-900/90" onClick={() => setCreating(true)}>
            <Plus size={14} /> New segment
          </Button>
        )}
      </div>

      {/* Create form */}
      {creating && (
        <div className="rounded-xl border bg-white p-5 mb-6">
          <h2 className="text-sm font-semibold text-slate-900 mb-4">New segment</h2>
          <div className="space-y-3 mb-4">
            <input
              type="text"
              placeholder="Segment name *"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
            />
            <input
              type="text"
              placeholder="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
            />
          </div>

          <div className="space-y-2 mb-3">
            {rules.map((rule, i) => (
              <FilterRow
                key={i}
                rule={rule}
                onUpdate={(r) => setRules((prev) => prev.map((x, j) => (j === i ? r : x)))}
                onRemove={() => setRules((prev) => prev.filter((_, j) => j !== i))}
              />
            ))}
          </div>

          <div className="flex items-center gap-3 mt-4">
            <Button size="sm" variant="outline" onClick={addRule}>
              <Plus size={13} /> Add filter
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setPreviewEnabled(true)}
            >
              <Eye size={13} /> Preview
            </Button>
            {preview != null && (
              <span className="text-xs text-slate-500">
                ~{preview.lead_count ?? 0} leads match
              </span>
            )}
            <div className="flex-1" />
            <Button size="sm" variant="ghost" onClick={() => setCreating(false)}>Cancel</Button>
            <Button
              size="sm"
              className="bg-brand-900 hover:bg-brand-900/90"
              onClick={handleCreate}
              disabled={createSegment.isPending || !name.trim()}
            >
              Create
            </Button>
          </div>
        </div>
      )}

      {/* Segments list */}
      {isLoading && <p className="text-sm text-slate-400">Loading…</p>}
      {!isLoading && (segments?.length ?? 0) === 0 && !creating && (
        <div className="rounded-xl border bg-white py-16 text-center text-sm text-slate-400">
          No segments yet. Create one to target leads for campaigns.
        </div>
      )}
      <div className="space-y-3">
        {(segments ?? []).map((seg: any) => (
          <div key={seg.id} className="rounded-xl border bg-white p-4 flex items-center justify-between">
            <div>
              <p className="font-medium text-slate-900 text-sm">{seg.name}</p>
              {seg.description && <p className="text-xs text-slate-400">{seg.description}</p>}
              <p className="text-xs text-slate-500 mt-0.5">
                {seg.lead_count ?? 0} leads · {Object.keys(seg.filter_rules ?? {}).length} filter{Object.keys(seg.filter_rules ?? {}).length !== 1 ? "s" : ""}
              </p>
            </div>
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={async () => {
                  const res = await segmentsApi.export(seg.id)
                  downloadBlob(new Blob([res.data]), `segment-${seg.name}.csv`)
                }}
              >
                <Download size={13} /> Export
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => deleteSegment.mutate(seg.id)}
                className="text-danger-700 hover:bg-danger-100"
              >
                <Trash2 size={13} />
              </Button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
