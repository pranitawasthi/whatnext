import { Heart, Plus, Star } from "lucide-react";
import type { Content, InteractionStatus } from "../types/api";
import { Button } from "./ui/button";
import { Card } from "./ui/card";
import { Select } from "./ui/select";

type Props = {
  item: Content;
  onLog?: (contentId: string, rating: number | null, status: InteractionStatus) => Promise<void>;
  busy?: boolean;
};

export function ContentCard({ item, onLog, busy }: Props) {
  return (
    <Card className="group min-w-64 max-w-80 overflow-hidden">
      <div className="aspect-[3/4] bg-zinc-900">
        {item.poster_url ? (
          <img src={item.poster_url} alt="" className="h-full w-full object-cover opacity-90 transition group-hover:scale-105" />
        ) : (
          <div className="flex h-full items-center justify-center text-zinc-600">{item.content_type}</div>
        )}
      </div>
      <div className="space-y-3 p-4">
        <div>
          <div className="flex items-start justify-between gap-2">
            <h3 className="line-clamp-2 text-base font-semibold">{item.title}</h3>
            {item.score ? <span className="text-xs text-rose-300">{Math.round(item.score * 100)}%</span> : null}
          </div>
          <p className="mt-1 text-xs uppercase tracking-wide text-zinc-500">
            {item.content_type} {item.release_year ? `/ ${item.release_year}` : ""}
          </p>
        </div>
        <p className="line-clamp-3 min-h-14 text-sm text-zinc-400">{item.description}</p>
        <div className="flex flex-wrap gap-1">
          {item.genres.slice(0, 3).map((genre) => (
            <span key={genre} className="rounded bg-zinc-800 px-2 py-1 text-xs text-zinc-300">
              {genre}
            </span>
          ))}
        </div>
        {item.explanation ? <p className="rounded border border-rose-900/60 bg-rose-950/30 p-2 text-xs text-rose-100">{item.explanation}</p> : null}
        {onLog ? (
          <LogControls contentId={item.id} onLog={onLog} busy={busy} />
        ) : (
          <div className="flex items-center gap-2 text-sm text-zinc-500">
            <Star className="h-4 w-4 text-amber-400" />
            {item.pacing}
          </div>
        )}
      </div>
    </Card>
  );
}

function LogControls({ contentId, onLog, busy }: { contentId: string; onLog: Props["onLog"]; busy?: boolean }) {
  const submit = async (status: InteractionStatus) => onLog?.(contentId, status === "favorite" ? 10 : 8, status);
  return (
    <div className="grid grid-cols-[1fr_auto_auto] gap-2">
      <Select
        defaultValue="watched"
        onChange={(event) => submit(event.target.value as InteractionStatus)}
        disabled={busy}
        aria-label="Log status"
      >
        <option value="watched">Watched</option>
        <option value="read">Read</option>
        <option value="liked">Liked</option>
        <option value="want_to_watch">Want watch</option>
        <option value="want_to_read">Want read</option>
        <option value="dropped">Dropped</option>
      </Select>
      <Button className="h-10 px-3" disabled={busy} onClick={() => submit("favorite")} title="Favorite">
        <Heart className="h-4 w-4" />
      </Button>
      <Button className="h-10 px-3 bg-zinc-800 hover:bg-zinc-700" disabled={busy} onClick={() => submit("watched")} title="Add">
        <Plus className="h-4 w-4" />
      </Button>
    </div>
  );
}
