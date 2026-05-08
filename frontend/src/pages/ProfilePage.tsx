import { useEffect, useState } from "react";
import { Star } from "lucide-react";
import { Card } from "../components/ui/card";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../lib/api";
import type { Interaction } from "../types/api";

export function ProfilePage() {
  const { user } = useAuth();
  const [items, setItems] = useState<Interaction[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .interactions()
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load profile"));
  }, []);

  return (
    <div className="space-y-5 pb-20">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-rose-400">{user?.email}</p>
        <h1 className="text-3xl font-bold">{user?.username}'s profile</h1>
      </div>
      {error ? <div className="rounded-md border border-rose-800 bg-rose-950/30 p-4 text-rose-100">{error}</div> : null}
      <div className="grid gap-3">
        {items.map((interaction) => (
          <Card key={interaction.id} className="grid gap-3 p-3 sm:grid-cols-[72px_1fr_auto]">
            <img src={interaction.content.poster_url ?? ""} alt="" className="h-24 w-16 rounded object-cover" />
            <div>
              <h2 className="font-semibold">{interaction.content.title}</h2>
              <p className="text-sm text-zinc-500">{interaction.content.content_type} / {interaction.status.replace(/_/g, " ")}</p>
              <p className="mt-2 line-clamp-2 text-sm text-zinc-400">{interaction.content.description}</p>
            </div>
            <div className="flex items-center gap-1 text-amber-300">
              <Star className="h-4 w-4" />
              {interaction.rating ?? "-"}
            </div>
          </Card>
        ))}
      </div>
      {!items.length && !error ? <div className="rounded-md border border-border p-6 text-zinc-400">Your shelf is empty.</div> : null}
    </div>
  );
}
