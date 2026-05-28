import { Routes, Route, Navigate } from "react-router-dom"
import { useAppStore } from "@/store"
import { Sidebar } from "@/components/layout/Sidebar"
import { Upload } from "@/pages/Upload"
import { Leads } from "@/pages/Leads"
import { Companies } from "@/pages/Companies"
import { Duplicates } from "@/pages/Duplicates"
import { Research } from "@/pages/Research"
import { Segments } from "@/pages/Segments"
import { KpiDashboard } from "@/pages/KpiDashboard"
import { Campaigns } from "@/pages/Campaigns"
import { Settings } from "@/pages/Settings"
import { AppLogs } from "@/pages/AppLogs"
import { Login } from "@/pages/Login"

function AuthLayout() {
  return (
    <div className="flex h-screen bg-slate-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/upload" element={<Upload />} />
          <Route path="/leads" element={<Leads />} />
          <Route path="/companies" element={<Companies />} />
          <Route path="/duplicates" element={<Duplicates />} />
          <Route path="/research" element={<Research />} />
          <Route path="/segments" element={<Segments />} />
          <Route path="/dashboard" element={<KpiDashboard />} />
          <Route path="/campaigns" element={<Campaigns />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/logs" element={<AppLogs />} />
          <Route path="*" element={<Navigate to="/upload" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  const token = useAppStore((s) => s.token)

  if (!token) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    )
  }

  return <AuthLayout />
}
