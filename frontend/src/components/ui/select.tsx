import type { SelectHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      className={cn(
        "h-10 rounded-md border border-border bg-zinc-950 px-3 text-sm text-foreground outline-none focus:border-rose-500",
        className,
      )}
      {...props}
    />
  );
}
