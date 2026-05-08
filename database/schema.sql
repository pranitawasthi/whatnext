-- SQLite reference schema. The app creates these tables automatically via SQLAlchemy.
CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(36) PRIMARY KEY,
  email VARCHAR(320) UNIQUE NOT NULL,
  username VARCHAR(80) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS content (
  id VARCHAR(36) PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  genres JSON NOT NULL,
  themes JSON NOT NULL,
  mood JSON NOT NULL,
  storytelling_style JSON NOT NULL,
  pacing VARCHAR(80) NOT NULL DEFAULT 'medium',
  release_year INTEGER,
  content_type VARCHAR(20) NOT NULL,
  poster_url TEXT,
  embedding JSON,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_interactions (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content_id VARCHAR(36) NOT NULL REFERENCES content(id) ON DELETE CASCADE,
  rating INTEGER CHECK (rating IS NULL OR (rating >= 1 AND rating <= 10)),
  status VARCHAR(30) NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_user_content_interaction UNIQUE (user_id, content_id)
);

CREATE TABLE IF NOT EXISTS recommendations (
  id VARCHAR(36) PRIMARY KEY,
  user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content_id VARCHAR(36) NOT NULL REFERENCES content(id) ON DELETE CASCADE,
  score DOUBLE PRECISION NOT NULL,
  explanation TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT uq_user_content_recommendation UNIQUE (user_id, content_id)
);

CREATE INDEX IF NOT EXISTS ix_content_type ON content(content_type);
CREATE INDEX IF NOT EXISTS ix_interactions_user ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS ix_recommendations_user ON recommendations(user_id);
