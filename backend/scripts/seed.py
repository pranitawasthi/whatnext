import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.session import AsyncSessionLocal
from app.models.content import Content
from app.repositories.content import ContentRepository
from app.services.ai import ai_service


SEED_CONTENT = [
    {
        "title": "Interstellar",
        "content_type": "movie",
        "release_year": 2014,
        "genres": ["science fiction", "drama", "adventure"],
        "themes": ["time dilation", "love", "survival", "cosmic mystery"],
        "mood": ["awe", "melancholy", "hopeful"],
        "storytelling_style": ["epic", "emotional", "high concept"],
        "pacing": "measured",
        "description": "A group of explorers travel through a wormhole to find humanity a new home while a father-daughter bond stretches across time.",
        "poster_url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=900&q=80",
    },
    {
        "title": "Foundation",
        "content_type": "tv",
        "release_year": 2021,
        "genres": ["science fiction", "space opera"],
        "themes": ["empire", "prophecy", "civilization", "mathematics"],
        "mood": ["grand", "political", "cerebral"],
        "storytelling_style": ["sweeping", "multi-generational", "philosophical"],
        "pacing": "slow burn",
        "description": "A band of exiles works to preserve knowledge as a galactic empire begins a long collapse predicted by psychohistory.",
        "poster_url": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=900&q=80",
    },
    {
        "title": "The Expanse",
        "content_type": "tv",
        "release_year": 2015,
        "genres": ["science fiction", "thriller", "political drama"],
        "themes": ["colonial tension", "alien technology", "survival", "class conflict"],
        "mood": ["tense", "gritty", "urgent"],
        "storytelling_style": ["ensemble", "realist", "serialized"],
        "pacing": "propulsive",
        "description": "A missing-person case exposes a conspiracy that could ignite war between Earth, Mars, and the Belt.",
        "poster_url": "https://images.unsplash.com/photo-1454789548928-9efd52dc4031?auto=format&fit=crop&w=900&q=80",
    },
    {
        "title": "Dune",
        "content_type": "book",
        "release_year": 1965,
        "genres": ["science fiction", "epic"],
        "themes": ["ecology", "destiny", "religion", "power"],
        "mood": ["mythic", "desert", "ominous"],
        "storytelling_style": ["dense", "political", "worldbuilding"],
        "pacing": "deliberate",
        "description": "A young heir is drawn into prophecy and political violence on a desert planet that controls the galaxy's most valuable resource.",
        "poster_url": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=900&q=80",
    },
    {
        "title": "The Three-Body Problem",
        "content_type": "book",
        "release_year": 2008,
        "genres": ["science fiction", "hard sci-fi"],
        "themes": ["first contact", "physics", "civilization", "existential risk"],
        "mood": ["cerebral", "ominous", "vast"],
        "storytelling_style": ["concept-driven", "mystery", "philosophical"],
        "pacing": "slow burn",
        "description": "A secretive scientific mystery links China's Cultural Revolution, a strange virtual world, and humanity's first contact with an unstable alien civilization.",
        "poster_url": "https://images.unsplash.com/photo-1465101162946-4377e57745c3?auto=format&fit=crop&w=900&q=80",
    },
    {
        "title": "Blade Runner 2049",
        "content_type": "movie",
        "release_year": 2017,
        "genres": ["science fiction", "neo-noir"],
        "themes": ["identity", "memory", "artificial life", "loneliness"],
        "mood": ["dark", "meditative", "melancholic"],
        "storytelling_style": ["visual", "atmospheric", "philosophical"],
        "pacing": "slow burn",
        "description": "A replicant investigator uncovers a buried secret that could destabilize the boundary between human and artificial life.",
        "poster_url": "https://images.unsplash.com/photo-1519608487953-e999c86e7455?auto=format&fit=crop&w=900&q=80",
    },
    {
        "title": "Severance",
        "content_type": "tv",
        "release_year": 2022,
        "genres": ["science fiction", "psychological thriller"],
        "themes": ["work", "identity", "memory", "corporate control"],
        "mood": ["eerie", "darkly funny", "unsettling"],
        "storytelling_style": ["mystery-box", "minimalist", "satirical"],
        "pacing": "controlled",
        "description": "Employees at a mysterious company undergo a procedure separating work memories from personal life, revealing a disturbing corporate experiment.",
        "poster_url": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?auto=format&fit=crop&w=900&q=80",
    },
    {
        "title": "Dark",
        "content_type": "tv",
        "release_year": 2017,
        "genres": ["science fiction", "mystery", "thriller"],
        "themes": ["time loops", "family secrets", "fate", "grief"],
        "mood": ["brooding", "tragic", "labyrinthine"],
        "storytelling_style": ["nonlinear", "complex", "philosophical"],
        "pacing": "intricate",
        "description": "A child's disappearance reveals a generational time-travel mystery binding four families in a small German town.",
        "poster_url": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?auto=format&fit=crop&w=900&q=80",
    },
]


async def main() -> None:
    async with AsyncSessionLocal() as db:
        repo = ContentRepository(db)
        for payload in SEED_CONTENT:
            embedding = await ai_service.embed_content_payload(payload)
            await repo.create(Content(**payload, embedding=embedding))
        await db.commit()


if __name__ == "__main__":
    asyncio.run(main())
