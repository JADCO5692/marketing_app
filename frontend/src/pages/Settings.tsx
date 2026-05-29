import { useState } from "react"
import { useSettings, useSaveSetting, useResetSetting } from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import { Save, RotateCcw, Eye, EyeOff, CheckCircle2, AlertCircle } from "lucide-react"

interface SettingItem {
  key: string
  label: string
  type: "secret" | "text" | "number" | "bool" | "textarea"
  description: string
  group: string
  value: string
  default?: string
  source: "db" | "env" | "unset"
  updated_at: string | null
}

function SourceBadge({ source }: { source: SettingItem["source"] }) {
  if (source === "db")    return <span className="rounded-full bg-brand-900/10 px-2 py-0.5 text-xs text-brand-900 font-medium">saved</span>
  if (source === "env")   return <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-500">.env default</span>
  return <span className="rounded-full bg-amber-50 px-2 py-0.5 text-xs text-amber-600">not set</span>
}

function SettingRow({ item }: { item: SettingItem }) {
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState("")
  const [show, setShow] = useState(false)
  const [saved, setSaved] = useState(false)

  const save = useSaveSetting()
  const reset = useResetSetting()

  const isSecret = item.type === "secret"
  const isBool = item.type === "bool"
  const isTextarea = item.type === "textarea"

  function startEdit() {
    if (isTextarea) {
      setDraft(item.source === "db" ? item.value : (item.default ?? ""))
    } else {
      setDraft("")
    }
    setEditing(true)
    setSaved(false)
  }

  async function handleSave() {
    if (!draft.trim()) return
    await save.mutateAsync({ key: item.key, value: draft.trim() })
    setEditing(false)
    setDraft("")
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  async function handleReset() {
    await reset.mutateAsync(item.key)
    setEditing(false)
    setDraft("")
  }

  const displayValue = item.value || (item.source === "unset" ? "" : "—")

  return (
    <div className="py-4 border-b last:border-b-0">
      <div className={`flex gap-4 ${isTextarea ? "flex-col" : "items-start justify-between"}`}>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="text-sm font-medium text-slate-900">{item.label}</span>
            <SourceBadge source={item.source} />
            {saved && <CheckCircle2 size={13} className="text-success-700" />}
          </div>
          <p className="text-xs text-slate-400 mb-2">{item.description}</p>

          {/* Current value display */}
          {!editing && (
            <div className="flex items-center gap-2">
              {item.source !== "unset" ? (
                isTextarea ? (
                  <pre className="rounded bg-slate-50 border px-3 py-2 text-xs text-slate-600 font-mono whitespace-pre-wrap max-h-24 overflow-hidden leading-relaxed w-full">
                    {displayValue}
                  </pre>
                ) : (
                  <code className="rounded bg-slate-50 border px-2 py-1 text-xs text-slate-600 font-mono">
                    {displayValue}
                  </code>
                )
              ) : (
                isTextarea && item.default ? (
                  <pre className="rounded bg-amber-50 border border-amber-100 px-3 py-2 text-xs text-slate-500 font-mono whitespace-pre-wrap max-h-24 overflow-hidden leading-relaxed w-full italic">
                    {item.default}
                  </pre>
                ) : (
                  <span className="text-xs text-slate-300 italic">not configured</span>
                )
              )}
              {isSecret && item.source !== "unset" && (
                <button
                  onClick={() => setShow((s) => !s)}
                  className="text-slate-300 hover:text-slate-500"
                >
                  {show ? <EyeOff size={13} /> : <Eye size={13} />}
                </button>
              )}
            </div>
          )}

          {/* Edit form */}
          {editing && (
            isTextarea ? (
              <div className="mt-2 space-y-2">
                <textarea
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  rows={16}
                  spellCheck={false}
                  autoFocus
                  className="w-full rounded-lg border px-3 py-2 text-xs font-mono text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-900 resize-y leading-relaxed"
                />
                <div className="flex items-center gap-2">
                  <Button size="sm" className="bg-brand-900 hover:bg-brand-900/90" onClick={handleSave} disabled={!draft.trim() || save.isPending}>
                    <Save size={12} /> Save
                  </Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>Cancel</Button>
                  {item.default && (
                    <button
                      type="button"
                      onClick={() => setDraft(item.default!)}
                      className="ml-auto text-xs text-slate-400 hover:text-slate-600 underline"
                    >
                      Reset to default
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2 mt-1">
                {isBool ? (
                  <select
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    className="rounded-lg border px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
                    autoFocus
                  >
                    <option value="">— select —</option>
                    <option value="true">true</option>
                    <option value="false">false</option>
                  </select>
                ) : (
                  <input
                    type={isSecret && !show ? "password" : "text"}
                    value={draft}
                    onChange={(e) => setDraft(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSave()}
                    placeholder={isSecret ? "Paste new key…" : "Enter value…"}
                    autoFocus
                    className="w-80 rounded-lg border px-3 py-1.5 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-brand-900"
                  />
                )}
                {isSecret && (
                  <button onClick={() => setShow((s) => !s)} className="text-slate-300 hover:text-slate-500">
                    {show ? <EyeOff size={13} /> : <Eye size={13} />}
                  </button>
                )}
                <Button size="sm" className="bg-brand-900 hover:bg-brand-900/90" onClick={handleSave} disabled={!draft.trim() || save.isPending}>
                  <Save size={12} /> Save
                </Button>
                <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>Cancel</Button>
              </div>
            )
          )}
        </div>

        {/* Action buttons */}
        {!editing && (
          <div className={`flex gap-1.5 shrink-0 ${isTextarea ? "self-start" : ""}`}>
            <Button size="sm" variant="outline" onClick={startEdit}>
              {item.source === "unset" ? "Set" : "Change"}
            </Button>
            {item.source === "db" && (
              <Button
                size="sm"
                variant="ghost"
                title="Reset to .env default"
                onClick={handleReset}
                disabled={reset.isPending}
                className="text-slate-400 hover:text-danger-700"
              >
                <RotateCcw size={13} />
              </Button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export function Settings() {
  const { data: items, isLoading } = useSettings()

  // Group items
  const groups: Record<string, SettingItem[]> = {}
  for (const item of (items ?? []) as SettingItem[]) {
    if (!groups[item.group]) groups[item.group] = []
    groups[item.group].push(item)
  }

  return (
    <div className="p-6 max-w-3xl">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          API keys and feature flags. Values saved here override the <code className="text-xs bg-slate-100 px-1 rounded">.env</code> file and persist in the database.
        </p>
      </div>

      {isLoading && <p className="text-sm text-slate-400">Loading…</p>}

      <div className="space-y-6">
        {Object.entries(groups).map(([group, groupItems]) => (
          <div key={group} className="rounded-xl border bg-white overflow-hidden">
            <div className="border-b bg-slate-50 px-5 py-3">
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">{group}</h2>
            </div>
            <div className="px-5">
              {groupItems.map((item) => (
                <SettingRow key={item.key} item={item} />
              ))}
            </div>
          </div>
        ))}
      </div>

      <p className="mt-6 text-xs text-slate-400">
        Changes take effect immediately — no restart needed. The API reads these values on every request.
      </p>
    </div>
  )
}
