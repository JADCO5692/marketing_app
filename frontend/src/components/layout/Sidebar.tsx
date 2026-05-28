import { NavLink } from "react-router-dom"
import { cn } from "@/lib/utils"
import {
  Upload, Users, Building2, Copy, Search, Layers, BarChart3, Mail,
  LogOut, Settings, ScrollText,
} from "lucide-react"
import { useAppStore } from "@/store"

const NAV = [
  { to: "/upload",    label: "Upload",        icon: Upload },
  { to: "/leads",     label: "Leads",         icon: Users },
  { to: "/companies", label: "Companies",     icon: Building2 },
  { to: "/duplicates",label: "Duplicates",    icon: Copy },
  { to: "/research",  label: "Research",      icon: Search },
  { to: "/segments",  label: "Segments",      icon: Layers },
  { to: "/dashboard", label: "KPI Dashboard", icon: BarChart3 },
  { to: "/campaigns", label: "Campaigns",     icon: Mail },
]

const ADMIN_NAV = [
  { to: "/settings",  label: "Settings",      icon: Settings },
  { to: "/logs",      label: "App Logs",      icon: ScrollText },
]

function NavItem({ to, label, icon: Icon }: { to: string; label: string; icon: React.ElementType }) {
  return (
    <NavLink
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
  )
}

export function Sidebar() {
  const logout = useAppStore((s) => s.logout)

  return (
    <aside className="flex h-screen w-56 flex-col border-r bg-white">
      {/* Logo */}
      <div className="flex h-14 items-center border-b px-5">
        <span className="text-sm font-bold text-brand-900 tracking-tight">Lead Intelligence</span>
      </div>

      {/* Main nav */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
        {NAV.map((item) => <NavItem key={item.to} {...item} />)}

        {/* Admin section */}
        <div className="pt-3 pb-1">
          <p className="px-3 text-xs font-medium text-slate-300 uppercase tracking-wider mb-1">Admin</p>
          {ADMIN_NAV.map((item) => <NavItem key={item.to} {...item} />)}
        </div>
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
