import axios from "axios"

const api = axios.create({
  baseURL: "/api/v1",
  headers: { "Content-Type": "application/json" },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token")
      window.location.href = "/login"
    }
    return Promise.reject(err)
  }
)

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  register: (data: { email: string; password: string; full_name?: string }) =>
    api.post("/auth/register", data),
  login: (data: { email: string; password: string }) =>
    api.post<{ access_token: string }>("/auth/login", data),
  me: () => api.get("/auth/me"),
}

// ── Upload ────────────────────────────────────────────────────────────────────
export const uploadApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append("file", file)
    return api.post("/upload/file", form, { headers: { "Content-Type": "multipart/form-data" } })
  },
  status: (id: string) => api.get(`/upload/jobs/${id}`),
  jobs: () => api.get("/upload/jobs"),
}

// ── Leads ─────────────────────────────────────────────────────────────────────
export const leadsApi = {
  list: (params?: Record<string, unknown>) => api.get("/leads", { params }),
  get: (id: string) => api.get(`/leads/${id}`),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/leads/${id}`, data),
  delete: (id: string) => api.delete(`/leads/${id}`),
  research: (id: string) => api.post(`/leads/${id}/research`),
  exportCsv: (params?: Record<string, unknown>) =>
    api.get("/leads/export", { params, responseType: "blob" }),
}

// ── Companies ─────────────────────────────────────────────────────────────────
export const companiesApi = {
  list: (params?: Record<string, unknown>) => api.get("/companies", { params }),
  get: (id: string) => api.get(`/companies/${id}`),
  leads: (id: string, params?: Record<string, unknown>) => api.get(`/companies/${id}/leads`, { params }),
  update: (id: string, data: Record<string, unknown>) => api.patch(`/companies/${id}`, data),
  research: (id: string) => api.post(`/companies/${id}/research`),
}

// ── Duplicates ────────────────────────────────────────────────────────────────
export const duplicatesApi = {
  list: (params?: Record<string, unknown>) => api.get("/duplicates", { params }),
  merge: (duplicateId: string, keepId: string) =>
    api.post(`/duplicates/${duplicateId}/merge`, { keep_id: keepId }),
  dismiss: (id: string) => api.post(`/duplicates/${id}/dismiss`),
}

// ── Segments ──────────────────────────────────────────────────────────────────
export const segmentsApi = {
  list: () => api.get("/segments"),
  create: (data: { name: string; description?: string; filter_rules: Record<string, unknown> }) =>
    api.post("/segments", data),
  get: (id: string) => api.get(`/segments/${id}`),
  leads: (id: string, params?: Record<string, unknown>) => api.get(`/segments/${id}/leads`, { params }),
  update: (id: string, data: Record<string, unknown>) => api.put(`/segments/${id}`, data),
  delete: (id: string) => api.delete(`/segments/${id}`),
  export: (id: string) => api.post(`/segments/${id}/export`, {}, { responseType: "blob" }),
  preview: (filterRules: Record<string, unknown>) =>
    api.post("/segments/preview", { filter_rules: filterRules }),
}

// ── Analytics ─────────────────────────────────────────────────────────────────
export const analyticsApi = {
  overview: () => api.get("/analytics/overview"),
  byIndustry: () => api.get("/analytics/by-industry"),
  byRegion: () => api.get("/analytics/by-region"),
  byFundingStage: () => api.get("/analytics/by-funding-stage"),
  byCompanySize: () => api.get("/analytics/by-company-size"),
  icpDistribution: () => api.get("/analytics/icp-distribution"),
  researchCost: () => api.get("/analytics/research-cost"),
}

// ── Research ──────────────────────────────────────────────────────────────────
export const researchApi = {
  list: (params?: Record<string, unknown>) => api.get("/research/logs", { params }),
  retryFailed: () => api.post("/research/retry-failed"),
}

// ── Admin ─────────────────────────────────────────────────────────────────────
export const adminApi = {
  listSettings: () => api.get("/admin/settings"),
  updateSetting: (key: string, value: string) => api.put(`/admin/settings/${key}`, { value }),
  deleteSetting: (key: string) => api.delete(`/admin/settings/${key}`),
  logs: (params?: Record<string, unknown>) => api.get("/admin/logs", { params }),
}

export default api
