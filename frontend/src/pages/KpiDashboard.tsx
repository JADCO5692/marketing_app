import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts"
import {
  useAnalyticsOverview, useAnalyticsByIndustry, useAnalyticsByRegion,
  useAnalyticsByFundingStage, useIcpDistribution, useResearchCost,
} from "@/hooks/useApi"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { KPI_TIPS } from "@/lib/kpi-tips"

const PALETTE = ["#0d1b4b", "#1b7a3b", "#2563eb", "#f39c12", "#c0392b", "#7c3aed", "#0891b2"]

function StatCard({
  label,
  value,
  tipKey,
  sub,
}: {
  label: string
  value: string | number
  tipKey?: string
  sub?: string
}) {
  return (
    <div className="rounded-xl border bg-white p-5" title={tipKey ? KPI_TIPS[tipKey] : undefined}>
      <p className="text-xs font-medium text-slate-400 mb-1">{label}</p>
      <p className="text-2xl font-bold text-slate-900">{value ?? "—"}</p>
      {sub && <p className="text-xs text-slate-400 mt-0.5">{sub}</p>}
    </div>
  )
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h2 className="text-sm font-semibold text-slate-700 mb-3 mt-6">{children}</h2>
}

export function KpiDashboard() {
  const { data: overview } = useAnalyticsOverview()
  const { data: byIndustry } = useAnalyticsByIndustry()
  const { data: byRegion } = useAnalyticsByRegion()
  const { data: byFunding } = useAnalyticsByFundingStage()
  const { data: icpDist } = useIcpDistribution()
  const { data: cost } = useResearchCost()

  const totalCost = cost?.reduce((s: number, c: any) => s + (c.total_cost ?? 0), 0) ?? 0
  const totalTokens = cost?.reduce((s: number, c: any) => s + (c.total_tokens ?? 0), 0) ?? 0

  return (
    <div className="p-6 max-w-6xl space-y-2">
      <h1 className="text-xl font-semibold text-slate-900">KPI Dashboard</h1>

      {/* Overview stats */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-4">
        <StatCard label="Total leads" value={overview?.total_leads ?? "—"} tipKey="lead_count" />
        <StatCard label="Enriched" value={overview?.enriched_leads ?? "—"} sub="research complete" />
        <StatCard
          label="Avg ICP score"
          value={overview?.avg_icp_score != null ? overview.avg_icp_score.toFixed(1) : "—"}
          tipKey="icp_score"
        />
        <StatCard
          label="Avg intent score"
          value={overview?.avg_intent_score != null ? overview.avg_intent_score.toFixed(1) : "—"}
          tipKey="intent_score"
        />
        <StatCard label="Decision makers" value={overview?.decision_makers ?? "—"} tipKey="is_decision_maker" />
        <StatCard label="Email verified" value={overview?.email_verified ?? "—"} tipKey="email_verified" />
        <StatCard
          label="Research cost"
          value={`$${totalCost.toFixed(2)}`}
          sub={`${(totalTokens / 1000).toFixed(1)}k tokens`}
        />
        <StatCard label="Duplicates" value={overview?.duplicates ?? "—"} />
      </div>

      {/* ICP distribution */}
      <SectionTitle>ICP Score Distribution</SectionTitle>
      <Card>
        <CardContent className="pt-4">
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={icpDist ?? []} barSize={36}>
              <XAxis dataKey="bucket" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip />
              <Bar dataKey="count" fill="#0d1b4b" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-2">
        {/* By Industry */}
        <div>
          <SectionTitle>Leads by Industry</SectionTitle>
          <Card>
            <CardContent className="pt-4">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart
                  data={(byIndustry ?? []).slice(0, 10)}
                  layout="vertical"
                  barSize={14}
                >
                  <XAxis type="number" tick={{ fontSize: 11 }} />
                  <YAxis
                    type="category"
                    dataKey="label"
                    width={110}
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip />
                  <Bar dataKey="count" fill="#2563eb" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* By Region */}
        <div>
          <SectionTitle>Leads by Region</SectionTitle>
          <Card>
            <CardContent className="pt-4">
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={(byRegion ?? []).slice(0, 8)}
                    dataKey="count"
                    nameKey="label"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label={({ label, percent }) =>
                      `${label} ${(percent * 100).toFixed(0)}%`
                    }
                    labelLine={false}
                  >
                    {(byRegion ?? []).slice(0, 8).map((_: any, i: number) => (
                      <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* By Funding Stage */}
        <div>
          <SectionTitle>Leads by Funding Stage</SectionTitle>
          <Card>
            <CardContent className="pt-4">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={byFunding ?? []} barSize={32}>
                  <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#1b7a3b" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Research cost by source */}
        <div>
          <SectionTitle>Research Cost by Source</SectionTitle>
          <Card>
            <CardContent className="pt-4">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={cost ?? []} barSize={32}>
                  <XAxis dataKey="source" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `$${v.toFixed(2)}`} />
                  <Tooltip formatter={(v: number) => [`$${v.toFixed(4)}`, "Cost"]} />
                  <Bar dataKey="total_cost" fill="#f39c12" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
