# How WhatNext Works Right Now

This document describes the current implementation state of the MVP.

## Stack

- Frontend: React, TypeScript, Tailwind CSS
- Backend: FastAPI, async SQLAlchemy
- Relational database: SQLite
- Vector database: Qdrant
- Embeddings: local `sentence-transformers` model `BAAI/bge-small-en-v1.5`
- Explanations: Groq chat API when `GROQ_API_KEY` is set
- Internet discovery:
  - Open Library for books
  - Apple iTunes Search API for movies and TV

## Runtime Services

Docker Compose runs:

- `frontend`: React app served on `http://localhost:8080`
- `backend`: FastAPI API on `http://localhost:8000`
- `qdrant`: vector database on `http://localhost:6333`

SQLite is stored in the Docker volume `sqlite_data`.
Qdrant vectors are stored in the Docker volume `qdrant_data`.
Hugging Face model files are cached in `hf_cache`.

## Startup Flow

When the backend starts:

1. FastAPI loads environment variables.
2. SQLAlchemy creates SQLite tables if they do not exist.
3. Qdrant collection `content_embeddings` is created if it does not exist.
4. API routes become available.

Relevant file:

```txt
backend/app/main.py
```

## Content Storage

Content is stored in SQLite in the `content` table.

Each content row has:

- title
- description
- genres
- themes
- mood
- storytelling style
- pacing
- release year
- content type: `book`, `movie`, or `tv`
- poster URL
- embedding JSON

The same content embedding is also inserted into Qdrant for similarity search.

Relevant files:

```txt
backend/app/models/content.py
backend/app/repositories/content.py
backend/app/services/vector_store.py
```

## Embeddings

Embeddings are generated locally with:

```txt
BAAI/bge-small-en-v1.5
```

This model outputs 384-dimensional vectors.

The embedding text is built from:

- title
- content type
- description
- genres
- themes
- mood
- storytelling style
- pacing

Relevant file:

```txt
backend/app/services/ai.py
```

## Authentication

Users can sign up and log in.

Passwords are hashed with bcrypt through Passlib.
JWT tokens are returned after signup/login.
Protected frontend routes use the JWT token from local storage.

Relevant files:

```txt
backend/app/core/security.py
backend/app/services/auth.py
backend/app/api/routes/auth.py
frontend/src/contexts/AuthContext.tsx
```

## User Interactions

Users can log content with:

- `favorite`
- `liked`
- `watched`
- `read`
- `dropped`
- `want_to_watch`
- `want_to_read`

Ratings are 1 to 10.

Interactions are stored in SQLite in `user_interactions`.

Relevant files:

```txt
backend/app/models/interaction.py
backend/app/repositories/interactions.py
frontend/src/components/ContentCard.tsx
```

## Search Flow

Search currently does two things:

1. Semantic local/vector search
2. Optional internet discovery

When a user searches:

1. Backend extracts keywords from the query.
2. If `include_internet` is true, backend searches:
   - Open Library for books
   - Apple iTunes Search API for movies and TV
3. Internet results are normalized into the app's content shape.
4. New internet results are embedded locally.
5. New internet results are saved into SQLite.
6. New vectors are saved into Qdrant.
7. The original query is embedded.
8. Qdrant returns semantically similar content.
9. Frontend displays:
   - results
   - keywords searched
   - local result count
   - internet import count

Relevant files:

```txt
backend/app/api/routes/search.py
backend/app/services/online_discovery.py
frontend/src/pages/SearchPage.tsx
```

Example request:

```json
{
  "query": "dark psychological sci-fi thriller",
  "limit": 18,
  "content_type": null,
  "include_internet": true
}
```

Example response shape:

```json
{
  "keywords": ["psychological", "sci-fi", "thriller", "dark"],
  "items": [],
  "local_count": 4,
  "internet_count": 6
}
```

## Recommendation Flow

Recommendations are based on the user's taste profile.

The profile includes:

- favorites
- liked items
- watched/read items
- want-to-watch/read items

Weights:

- favorite = 5.0
- liked = 3.0
- watched/read = 1.0
- want_to_watch/want_to_read = 0.8

Rating also adds a small boost or penalty.

When recommendations are requested:

1. Backend loads the user's interaction history.
2. It builds a weighted average user embedding.
3. It extracts taste keywords from the user's saved items.
4. It searches the internet with those taste keywords.
5. Any new internet results are imported into SQLite and Qdrant.
6. Qdrant searches for similar content.
7. Already-saved user items are excluded.
8. Results are ranked by vector similarity.
9. Groq generates explanations if `GROQ_API_KEY` is configured.
10. Recommendations are cached in SQLite.

Relevant files:

```txt
backend/app/services/recommendations.py
backend/app/api/routes/recommendations.py
backend/app/services/online_discovery.py
```

## Groq Usage

Groq is used only for explanation text.

It does not generate embeddings.
Embeddings are local.

If `GROQ_API_KEY` is missing or Groq fails, the backend returns a fallback explanation.

Relevant file:

```txt
backend/app/services/ai.py
```

## Seed Data

The seed script inserts sample content such as:

- Interstellar
- Foundation
- The Expanse
- Dune
- The Three-Body Problem
- Blade Runner 2049
- Severance
- Dark

The seed script also embeds each item and stores the vector in Qdrant.

Run:

```bash
docker compose exec backend python scripts/seed.py
```

If import issues appear, use:

```bash
docker compose exec backend sh -lc "PYTHONPATH=/app python scripts/seed.py"
```

## Run Commands

Start everything:

```bash
docker compose up --build
```

Seed data:

```bash
docker compose exec backend python scripts/seed.py
```

Open the app:

```txt
http://localhost:8080
```

Open API docs:

```txt
http://localhost:8000/docs
```

Rebuild backend after dependency changes:

```bash
docker compose build --no-cache backend
docker compose up
```

Reset all persisted data:

```bash
docker compose down -v
docker compose up --build
docker compose exec backend python scripts/seed.py
```

## Current Limitations

- Internet movie/TV search uses Apple iTunes API, not TMDB.
- Internet discovery metadata can be sparse for mood, pacing, and storytelling style.
- Recommendations improve as more content is imported and logged.
- Groq explanations depend on the API key and network availability.
- Search imports internet results into the catalog automatically.
- Duplicate detection is title/type/year based, not provider-ID based yet.

## Best Test Path

1. Start Docker Compose.
2. Seed content.
3. Create an account.
4. Search for `dark psychological sci-fi thriller` with internet enabled.
5. Add a few results to `favorite`, `liked`, or `want_to_watch`.
6. Go to Recommendations.
7. Click refresh.
8. Check that recommendations include Groq explanations and reflect your watchlist.
