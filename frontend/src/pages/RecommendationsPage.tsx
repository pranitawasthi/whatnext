import { Loader2, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";
import { ContentCard } from "../components/ContentCard";
import { Button } from "../components/ui/button";
import { Select } from "../components/ui/select";
import { api } from "../lib/api";
import type { Content } from "../types/api";

export function RecommendationsPage() {
  const [items, setItems] = useState<Content[]>([]);
  const [contentType, setContentType] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function load(refresh = false) {
    setLoading(true);
    setError("");
    try {
      setItems(await api.recommendations(refresh, contentType));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate recommendations");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load(false);
  }, [contentType]);

  return (
    <div className="space-y-5 pb-20">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-rose-400">Vector-ranked for you</p>
          <h1 className="text-3xl font-bold">Recommendations</h1>
        </div>
        <div className="flex gap-2">
          <Select value={contentType} onChange={(event) => setContentType(event.target.value)}>
            <option value="">All media</option>
            <option value="movie">Movies</option>
            <option value="tv">TV</option>
            <option value="book">Books</option>
          </Select>
          <Button onClick={() => load(true)} disabled={loading} title="Refresh">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
          </Button>
        </div>
      </div>
      {error ? <div className="rounded-md border border-rose-800 bg-rose-950/30 p-4 text-rose-100">{error}</div> : null}
      {!loading && !items.length ? (
        <div className="rounded-md border border-border bg-muted p-6 text-zinc-300">Favorite or like a few items on the dashboard to build your taste profile.</div>
      ) : null}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {items.map((item) => (
          <ContentCard key={item.id} item={item} />
        ))}
      </div>
    </div>
  );
}
