import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { authApi } from "@/lib/api"
import { useAppStore } from "@/store"
import { Button } from "@/components/ui/button"

export function Login() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const setToken = useAppStore((s) => s.setToken)
  const setUser = useAppStore((s) => s.setUser)
  const navigate = useNavigate()

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      const res = await authApi.login({ email, password })
      setToken(res.data.access_token)
      const me = await authApi.me()
      setUser(me.data)
      navigate("/upload")
    } catch {
      setError("Invalid email or password")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50">
      <div className="w-full max-w-sm rounded-xl border bg-white p-8 shadow-sm">
        <h1 className="mb-1 text-lg font-bold text-brand-900">Lead Intelligence</h1>
        <p className="mb-6 text-sm text-slate-500">Sign in to your account</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-900"
            />
          </div>
          {error && <p className="text-xs text-danger-700">{error}</p>}
          <Button type="submit" disabled={loading} className="w-full bg-brand-900 hover:bg-brand-900/90">
            {loading ? "Signing in…" : "Sign in"}
          </Button>
        </form>
      </div>
    </div>
  )
}
