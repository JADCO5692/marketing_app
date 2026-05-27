import { create } from "zustand"

interface User {
  id: string
  email: string
  full_name: string | null
  is_superuser: boolean
}

interface AppStore {
  user: User | null
  setUser: (u: User | null) => void
  token: string | null
  setToken: (t: string | null) => void
  logout: () => void
}

export const useAppStore = create<AppStore>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  token: localStorage.getItem("token"),
  setToken: (token) => {
    if (token) localStorage.setItem("token", token)
    else localStorage.removeItem("token")
    set({ token })
  },
  logout: () => {
    localStorage.removeItem("token")
    set({ user: null, token: null })
  },
}))
