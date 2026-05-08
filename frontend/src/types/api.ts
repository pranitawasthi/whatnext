export type User = {
  id: string;
  email: string;
  username: string;
};

export type ContentType = "book" | "movie" | "tv";

export type Content = {
  id: string;
  title: string;
  description: string;
  genres: string[];
  themes: string[];
  mood: string[];
  storytelling_style: string[];
  pacing: string;
  release_year: number | null;
  content_type: ContentType;
  poster_url: string | null;
  score?: number | null;
  explanation?: string | null;
};

export type InteractionStatus =
  | "favorite"
  | "liked"
  | "watched"
  | "read"
  | "dropped"
  | "want_to_watch"
  | "want_to_read";

export type Interaction = {
  id: string;
  rating: number | null;
  status: InteractionStatus;
  content: Content;
};

export type Paginated<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
};

export type SearchResponse = {
  keywords: string[];
  items: Content[];
  local_count: number;
  internet_count: number;
};
