import { Mail, Clock } from "lucide-react"

export function Campaigns() {
  return (
    <div className="p-8 max-w-xl">
      <h1 className="text-xl font-semibold text-slate-900 mb-1">Campaigns</h1>
      <p className="text-sm text-slate-500 mb-8">Email campaign targeting and automation</p>

      <div className="rounded-xl border-2 border-dashed border-slate-200 py-16 text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
          <Mail size={22} className="text-slate-400" />
        </div>
        <h2 className="text-sm font-semibold text-slate-700 mb-1">Coming in v0.2.0</h2>
        <p className="text-xs text-slate-400 max-w-xs mx-auto">
          Campaign builder, template editor, send scheduling, and open/click tracking
          will be available once lead enrichment is complete.
        </p>
        <div className="mt-4 flex items-center justify-center gap-1.5 text-xs text-slate-400">
          <Clock size={12} />
          Segment your leads first → then launch targeted campaigns
        </div>
      </div>
    </div>
  )
}
