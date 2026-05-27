import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat("en-US", { year: "numeric", month: "short", day: "numeric" }).format(new Date(date))
}

export function formatScore(score: number | null | undefined): string {
  if (score == null) return "—"
  return score.toFixed(0)
}

export function scoreLabel(score: number | null | undefined): "hot" | "warm" | "cold" | "none" {
  if (score == null) return "none"
  if (score >= 70) return "hot"
  if (score >= 40) return "warm"
  return "cold"
}

export function scoreColorClass(score: number | null | undefined): string {
  const label = scoreLabel(score)
  return {
    hot: "text-success-700",
    warm: "text-warning-500",
    cold: "text-danger-700",
    none: "text-slate-400",
  }[label]
}

export function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
