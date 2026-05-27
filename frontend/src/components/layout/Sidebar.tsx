import { NavLink } from "react-router-dom"
import { cn } from "@/lib/utils"
import {
  Upload, Users, Building2, Copy, Search, Layers, BarChart3, Mail, LogOut,
} from "lucide-react"
import { useAppStore } from "@/store"

const NAV = [
  { to: "/upload",    label: "Upload",      icon: Upload },
  { to: "/leads",     label: "Leads",       icon: Users },
  { to: "/companies", label: "Companies",   icon: Building2 },
  { to: "/duplicates",label: "Duplicates",  icon: Copy },
  { to: "/research",  label: "Research",    icon: Search },
  { to: "/segments",  label: "Segments",    icon: Layers },
  { to: "/dashboard", label: "KPI Dashboard", icon: BarChart3 },
  { to: "/campaigns", label: "Campaigns",   icon: Mail },
]

export function Sidebar() {
  const logout = useAppStore((s) => s.logout)

  return (
    <aside className="flex h-screen w-56 flex-col border-r bg-white">
      {/* Logo */}
      <div className="flex h-14 items-center border-b px-5">
        <span className="text-sm font-bold text-brand-900 tracking-tight">Lead Intelligence</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors duration-150",
                isActive
                  ? "bg-brand-900 text-white font-medium"
                  : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
              )
            }
          >
            <Icon size={16} />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="border-t p-3">
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 transition-colors duration-150"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </aside>
  )
}
