import { FormEvent, useState } from "react";
import { Loader2, Search } from "lucide-react";
import { ContentCard } from "../components/ContentCard";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Select } from "../components/ui/select";
import { api } from "../lib/api";
import type { Content } from "../types/api";
import { useContentActions } from "../hooks/useContentActions";

export function SearchPage() {
  const [query, setQuery] = useState("dark psychological sci-fi thriller");
  const [contentType, setContentType] = useState("");
  const [items, setItems] = useState<Content[]>([]);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [includeInternet, setIncludeInternet] = useState(true);
  const [counts, setCounts] = useState({ local: 0, internet: 0 });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { log, message } = useContentActions();

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      const response = await api.search(query, contentType, includeInternet);
      setItems(response.items);
      setKeywords(response.keywords);
      setCounts({ local: response.local_count, internet: response.internet_count });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-5 pb-20">
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-rose-400">Semantic search</p>
        <h1 className="text-3xl font-bold">Search by vibe, theme, or plot memory</h1>
      </div>
      <form onSubmit={submit} className="grid gap-2 rounded-md border border-border bg-muted p-3 md:grid-cols-[1fr_160px_auto_auto]">
        <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="philosophical space opera with slow burn politics" />
        <Select value={contentType} onChange={(event) => setContentType(event.target.value)}>
          <option value="">All</option>
          <option value="movie">Movies</option>
          <option value="tv">TV</option>
          <option value="book">Books</option>
        </Select>
        <label className="flex h-10 items-center gap-2 rounded-md border border-border bg-zinc-950 px-3 text-sm text-zinc-300">
          <input
            type="checkbox"
            checked={includeInternet}
            onChange={(event) => setIncludeInternet(event.target.checked)}
            className="h-4 w-4 accent-rose-600"
          />
          Internet
        </label>
        <Button disabled={loading}>
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          Search
        </Button>
      </form>
      {keywords.length ? (
        <div className="flex flex-wrap items-center gap-2 text-sm text-zinc-400">
          <span>Keywords searched:</span>
          {keywords.map((keyword) => (
            <span key={keyword} className="rounded bg-zinc-800 px-2 py-1 text-xs text-zinc-200">
              {keyword}
            </span>
          ))}
          <span className="text-zinc-500">
            {counts.internet} internet imports / {counts.local} local matches
          </span>
        </div>
      ) : null}
      {message ? <div className="rounded-md bg-emerald-950 px-3 py-2 text-sm text-emerald-200">{message}</div> : null}
      {error ? <div className="rounded-md border border-rose-800 bg-rose-950/30 p-4 text-rose-100">{error}</div> : null}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {items.map((item) => (
          <ContentCard key={item.id} item={item} onLog={log} />
        ))}
      </div>
    </div>
  );
}
