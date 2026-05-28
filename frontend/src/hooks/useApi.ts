import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"
import {
  leadsApi, companiesApi, duplicatesApi, segmentsApi,
  analyticsApi, researchApi, uploadApi, adminApi,
} from "@/lib/api"

// ── Leads ──────────────────────────────────────────────────────────────────
export function useLeads(params: Record<string, unknown> = {}) {
  return useQuery({
    queryKey: ["leads", params],
    queryFn: () => leadsApi.list(params).then((r) => r.data),
  })
}

export function useLead(id: string) {
  return useQuery({
    queryKey: ["leads", id],
    queryFn: () => leadsApi.get(id).then((r) => r.data),
    enabled: !!id,
  })
}

export function useUpdateLead() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      leadsApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["leads"] }),
  })
}

export function useDeleteLead() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => leadsApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["leads"] })
      toast.success("Lead deleted")
    },
    onError: () => toast.error("Failed to delete lead"),
  })
}

export function useResearchLead() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => leadsApi.research(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["leads"] })
      toast.success("Research queued", { description: "The lead will be enriched in the background." })
    },
    onError: () => toast.error("Failed to queue research"),
  })
}

// ── Companies ──────────────────────────────────────────────────────────────
export function useCompanies(params: Record<string, unknown> = {}) {
  return useQuery({
    queryKey: ["companies", params],
    queryFn: () => companiesApi.list(params).then((r) => r.data),
  })
}

export function useCompany(id: string) {
  return useQuery({
    queryKey: ["companies", id],
    queryFn: () => companiesApi.get(id).then((r) => r.data),
    enabled: !!id,
  })
}

export function useCompanyLeads(companyId: string, params: Record<string, unknown> = {}) {
  return useQuery({
    queryKey: ["companies", companyId, "leads", params],
    queryFn: () => companiesApi.leads(companyId, params).then((r) => r.data),
    enabled: !!companyId,
  })
}

// ── Duplicates ─────────────────────────────────────────────────────────────
export function useDuplicates(params: Record<string, unknown> = {}) {
  return useQuery({
    queryKey: ["duplicates", params],
    queryFn: () => duplicatesApi.list(params).then((r) => r.data),
  })
}

export function useMergeDuplicate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ duplicateId, keepId }: { duplicateId: string; keepId: string }) =>
      duplicatesApi.merge(duplicateId, keepId),

    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["duplicates"] })
      qc.invalidateQueries({ queryKey: ["leads"] })
    },
  })
}

export function useDismissDuplicate() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (duplicateId: string) => duplicatesApi.dismiss(duplicateId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["duplicates"] }),
  })
}

// ── Segments ───────────────────────────────────────────────────────────────
export function useSegments() {
  return useQuery({
    queryKey: ["segments"],
    queryFn: () => segmentsApi.list().then((r) => r.data),
  })
}

export function useSegmentPreview(filterRules: Record<string, unknown>, enabled: boolean) {
  return useQuery({
    queryKey: ["segments", "preview", filterRules],
    queryFn: () => segmentsApi.preview(filterRules).then((r) => r.data),
    enabled,
  })
}

export function useCreateSegment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: Record<string, unknown>) => segmentsApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["segments"] }),
  })
}

export function useDeleteSegment() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => segmentsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["segments"] }),
  })
}

// ── Analytics ──────────────────────────────────────────────────────────────
export function useAnalyticsOverview() {
  return useQuery({
    queryKey: ["analytics", "overview"],
    queryFn: () => analyticsApi.overview().then((r) => r.data),
    staleTime: 60_000,
  })
}

export function useAnalyticsByIndustry() {
  return useQuery({
    queryKey: ["analytics", "by-industry"],
    queryFn: () => analyticsApi.byIndustry().then((r) => r.data),
    staleTime: 60_000,
  })
}

export function useAnalyticsByRegion() {
  return useQuery({
    queryKey: ["analytics", "by-region"],
    queryFn: () => analyticsApi.byRegion().then((r) => r.data),
    staleTime: 60_000,
  })
}

export function useAnalyticsByFundingStage() {
  return useQuery({
    queryKey: ["analytics", "by-funding-stage"],
    queryFn: () => analyticsApi.byFundingStage().then((r) => r.data),
    staleTime: 60_000,
  })
}

export function useAnalyticsByCompanySize() {
  return useQuery({
    queryKey: ["analytics", "by-company-size"],
    queryFn: () => analyticsApi.byCompanySize().then((r) => r.data),
    staleTime: 60_000,
  })
}

export function useIcpDistribution() {
  return useQuery({
    queryKey: ["analytics", "icp-distribution"],
    queryFn: () => analyticsApi.icpDistribution().then((r) => r.data),
    staleTime: 60_000,
  })
}

export function useResearchCost() {
  return useQuery({
    queryKey: ["analytics", "research-cost"],
    queryFn: () => analyticsApi.researchCost().then((r) => r.data),
    staleTime: 60_000,
  })
}

// ── Research Logs ──────────────────────────────────────────────────────────
export function useResearchLogs(params: Record<string, unknown> = {}) {
  return useQuery({
    queryKey: ["research-logs", params],
    queryFn: () => researchApi.list(params).then((r) => r.data),
  })
}

export function useRetryFailed() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => researchApi.retryFailed(),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["research-logs"] }),
  })
}

// ── Upload ─────────────────────────────────────────────────────────────────
export function useUploadCsv() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (file: File) => uploadApi.upload(file),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["leads"] }),
  })
}

// ── Admin: Settings ───────────────────────────────────────────────────────────
export function useSettings() {
  return useQuery({
    queryKey: ["admin", "settings"],
    queryFn: () => adminApi.listSettings().then((r) => r.data),
  })
}

export function useSaveSetting() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ key, value }: { key: string; value: string }) =>
      adminApi.updateSetting(key, value),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "settings"] }),
  })
}

export function useResetSetting() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (key: string) => adminApi.deleteSetting(key),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["admin", "settings"] }),
  })
}

// ── Admin: App Logs ───────────────────────────────────────────────────────────
export function useAppLogs(params: Record<string, unknown> = {}, autoRefresh: boolean = false) {
  return useQuery({
    queryKey: ["admin", "logs", params],
    queryFn: () => adminApi.logs(params).then((r) => r.data),
    refetchInterval: autoRefresh ? 3000 : false,
  })
}

export function useUploadJob(jobId: string | null) {
  return useQuery({
    queryKey: ["upload-job", jobId],
    queryFn: () => uploadApi.status(jobId!).then((r) => r.data),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === "processing" ? 1500 : false
    },
  })
}
