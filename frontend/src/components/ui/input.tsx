import type { InputHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "h-10 w-full rounded-md border border-border bg-zinc-950 px-3 text-sm text-foreground outline-none transition placeholder:text-zinc-500 focus:border-rose-500",
        className,
      )}
      {...props}
    />
  );
}
