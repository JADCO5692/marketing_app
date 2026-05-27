import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "bg-primary/10 text-primary",
        hot: "bg-success-100 text-success-700",
        warm: "bg-warning-100 text-warning-500",
        cold: "bg-danger-100 text-danger-700",
        raw: "bg-slate-100 text-slate-500",
        researching: "bg-blue-100 text-blue-600 animate-pulse",
        enriched: "bg-success-100 text-success-700",
        duplicate: "bg-amber-100 text-amber-600",
        merged: "bg-purple-100 text-purple-600",
        invalid: "bg-danger-100 text-danger-700",
        outline: "border border-current bg-transparent",
      },
    },
    defaultVariants: { variant: "default" },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />
}

export { Badge, badgeVariants }
