import { useEffect, useMemo, useState } from "react";
import { api } from "../lib/api";
import type { Content } from "../types/api";
import { Carousel } from "../components/Carousel";
import { useContentActions } from "../hooks/useContentActions";

export function DashboardPage() {
  const [items, setItems] = useState<Content[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const { log, message } = useContentActions();

  useEffect(() => {
    api
      .listContent()
      .then((response) => setItems(response.items))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load content"))
      .finally(() => setLoading(false));
  }, []);

  const byType = useMemo(
    () => ({
      movie: items.filter((item) => item.content_type === "movie"),
      tv: items.filter((item) => item.content_type === "tv"),
      book: items.filter((item) => item.content_type === "book"),
    }),
    [items],
  );

  if (loading) return <State text="Loading the catalog..." />;
  if (error) return <State text={error} error />;

  return (
    <div className="space-y-8 pb-20">
      <section className="grid gap-4 rounded-md border border-border bg-zinc-950 p-6 md:grid-cols-[1.3fr_0.7fr]">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-rose-400">Taste starts with a few signals</p>
          <h1 className="mt-2 text-3xl font-bold">Add favorites, rate what landed, and let the vector search do the quiet work.</h1>
        </div>
        <div className="flex items-end justify-start md:justify-end">
          {message ? <span className="rounded-md bg-emerald-950 px-3 py-2 text-sm text-emerald-200">{message}</span> : null}
        </div>
      </section>
      <Carousel title="Movies" items={byType.movie} onLog={log} />
      <Carousel title="TV Shows" items={byType.tv} onLog={log} />
      <Carousel title="Books" items={byType.book} onLog={log} />
    </div>
  );
}

function State({ text, error }: { text: string; error?: boolean }) {
  return <div className={`rounded-md border border-border p-6 ${error ? "text-rose-200" : "text-zinc-400"}`}>{text}</div>;
}
