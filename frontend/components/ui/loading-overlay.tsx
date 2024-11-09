"use client"

import * as React from "react"
import { Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"

interface LoadingOverlayProps extends React.HTMLAttributes<HTMLDivElement> {
  message?: string
  isLoading?: boolean
}

const LoadingOverlay = React.forwardRef<HTMLDivElement, LoadingOverlayProps>(
  ({ className, message = "Loading...", isLoading = true, ...props }, ref) => {
    if (!isLoading) return null

    return (
      <div
        ref={ref}
        className={cn(
          "fixed inset-0 bg-background/80 backdrop-blur-sm z-50",
          "data-[state=open]:animate-in data-[state=closed]:animate-out",
          "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
          className
        )}
        {...props}
      >
        <div className="fixed left-[50%] top-[50%] translate-x-[-50%] translate-y-[-50%]">
          <div className="mx-auto flex flex-col items-center justify-center gap-4">
            <Loader2 className="h-8 w-8 animate-spin" />
            <p className="text-sm font-medium text-muted-foreground">{message}</p>
          </div>
        </div>
      </div>
    )
  }
)
LoadingOverlay.displayName = "LoadingOverlay"

export { LoadingOverlay } 