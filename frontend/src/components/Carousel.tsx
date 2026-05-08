import type { Content, InteractionStatus } from "../types/api";
import { ContentCard } from "./ContentCard";

export function Carousel({
  title,
  items,
  onLog,
}: {
  title: string;
  items: Content[];
  onLog?: (contentId: string, rating: number | null, status: InteractionStatus) => Promise<void>;
}) {
  return (
    <section className="space-y-3">
      <h2 className="text-xl font-semibold">{title}</h2>
      <div className="scrollbar-none flex gap-4 overflow-x-auto pb-2">
        {items.map((item) => (
          <ContentCard key={item.id} item={item} onLog={onLog} />
        ))}
      </div>
    </section>
  );
}
