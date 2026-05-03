# Methodology Implementation Gaps & How To Implement Them (Aptiverse V1)

**Date:** May 1, 2026  
**Scope:** This document compares the *Methodology* section you shared against what is currently implemented in this repository, and outlines concrete steps to implement the missing pieces using the existing FastAPI + SQLAlchemy codebase.

---

## Executive summary

### Implemented (partially or differently than described)
- **Personalization:** Weak-topic detection and daily practice set generation exist, but are **aggregate/statistics-based** (not BKT).
- **Battle module:** Real-time battles via **FastAPI WebSockets** exist, but battle state + leaderboard are **in-memory** (not Redis).
- **Gamification:** XP, streaks, levels, badges exist, but are **synchronous/monolith** (not Kafka EDA).
- **Vector search:** Weaviate + ChromaDB services exist, but production wiring is inconsistent; some code paths use a stub client.
- **Community discussions:** Discussion + voting endpoints exist (a “hub-like” feature), but **semantic + lexical hybrid search** is not implemented.

### Not implemented (major gaps vs the methodology)
- **BKT learner model** (mastery probabilities per skill/topic).
- **Celery** task queue for scheduling (and Celery Beat for reminders).
- **Twilio + SendGrid** reminder dispatch.
- **Open-source LLM generation pipeline** (LLaMA/Mistral) and **PEFT/LoRA** fine-tuning.
- **Kafka-based event-driven architecture** (producers/consumers, microservices).
- **Redis-backed ephemeral state** for battle rooms/leaderboards.
- **Hybrid lexical + semantic search** (Postgres full-text + vector DB) for a true Knowledge Hub.

---

## 1) Predictive Personalization & Scheduling Engine (BKT + async reminders)

### What the methodology claims
- **Core Logic:** Bayesian Knowledge Tracing (BKT) model (Scikit-learn) using performance vectors (accuracy, latency, time decay) to output real-time mastery probabilities.
- **Architecture:** FastAPI inference endpoints + Celery task queue for personalized quiz generation + Twilio (SMS) + SendGrid (Email) reminders.
- **Function:** Identify weak areas and trigger remediation + alerts.

### What is implemented today
- **Weak areas** are computed via **simple topic-level aggregates (accuracy thresholding)** in `backend/ml_service.py`.
- **Daily practice sets** are generated from weak topics in `backend/ml_service.py` and returned by `backend/main.py` endpoints.
- Personalization caching is done via **in-process dictionaries**, not Redis.

### What is missing / inaccurate vs methodology
- No BKT implementation (no per-topic latent mastery probability, no BKT parameters).
- No time-decay or latency feature integration for mastery estimation.
- No Celery worker/beat, no async reminder jobs.
- No Twilio/SendGrid integrations.
- There is a **broken reference**: `/weak-areas` calls `ml_service.get_user_weak_areas(...)`, but that function does not exist.

### How to implement it (recommended approach)

#### A. Data model changes
Add a durable mastery state table.

- New table: `user_topic_mastery`
  - `id`
  - `user_id`
  - `topic` (or `skill_id`)
  - `p_mastery` (float 0..1)
  - `updated_at`
  - Optional: store BKT parameters per topic (`p_init`, `p_learn`, `p_guess`, `p_slip`, `forget_lambda`)

This keeps the model state persistent and enables real-time inference without reprocessing the entire history.

#### B. Implement BKT (don’t force Scikit-learn)
Classic BKT is **not a native Scikit-learn estimator**. In practice, implement BKT update equations directly.

A reasonable minimal BKT-like update loop:
- Maintain $P(L)$ = probability the user has learned the topic.
- Parameters:
  - `p_guess`, `p_slip` (observation model)
  - `p_learn` (learning transition)
  - `forget_lambda` (time-based forgetting)
- Update on each attempt:
  1. Posterior after observation (correct/incorrect)
  2. Transition with learning + forgetting driven by $
0$ time gap

Latency can affect confidence:
- Slow correct answers can down-weight the update (or increase slip).

#### C. Endpoint + integration points
- Fix `/weak-areas` to call a real function.
- Add a mastery endpoint:
  - `GET /personalization/mastery`
- Update mastery in existing flows:
  - on `POST /submit-answer` (after recording attempt)

#### D. Celery scheduling + reminders
1. Add dependencies: `celery`, `redis` (broker), optionally `flower`.
2. Add files:
   - `backend/celery_app.py`
   - `backend/tasks.py`
3. Add tasks:
   - `generate_daily_practice_set_for_user(user_id)`
   - `send_reminder_email(user_id)`
   - `send_reminder_sms(user_id)`
4. Add **Celery Beat** schedule:
   - Daily reminders by local time
   - “nudge” if user inactive by time threshold

#### E. Twilio + SendGrid
Implement a single abstraction:
- `backend/notifications.py`:
  - `send_email_sendgrid(...)`
  - `send_sms_twilio(...)`

Environment variables:
- `SENDGRID_API_KEY`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_NUMBER`

Keep Gmail SMTP only as dev fallback if you want.

#### F. Runtime infrastructure
Current `docker-compose.yml` runs backend + frontend only and uses SQLite. To support Celery scheduling:
- Add `redis` service.
- Add `celery_worker` and `celery_beat` services.

---

## 2) Adaptive Content Generation (ACG) Pipeline (Open LLMs + LoRA/PEFT + vector cache)

### What the methodology claims
- Open-source LLM generation (LLaMA-3/Mistral) fine-tuned with LoRA/PEFT.
- Vector DB (Weaviate/Milvus) semantic cache for duplicate prevention (ANN).
- PostgreSQL persistence for validated content.

### What is implemented today
- There is an **offline generation script** in `backend/synth_data.py` using **Google Gemini** (not LLaMA/Mistral, not LoRA/PEFT).
- Vector DB services exist:
  - Weaviate: `backend/weaviate_service.py`
  - ChromaDB: `backend/vector_service.py`

### What is missing / inaccurate vs methodology
- No LoRA/PEFT training or model serving.
- No open-source LLM inference service.
- Semantic duplicate detection is **not reliably wired**:
  - `backend/admin_routes.py` imports `get_weaviate_client` from `backend/ml_service.py`, but that function is a **stub that returns None**, so Weaviate duplicate checks do not run.
  - Additionally, `admin_routes.py` appears to use an older-style Weaviate query API, while `weaviate_service.py` uses the newer v4 client API.

### How to implement it (phased)

#### Phase 1: Make duplicate detection actually work
Pick one vector backend and wire all code paths to it.

Option A (matches write-up): **Weaviate**
- Replace the stub client usage in admin upload:
  - Use `backend/weaviate_service.py:get_weaviate_client()`
- Ensure schema creation runs (startup hook or admin command).

Option B (fast dev): **ChromaDB**
- Use `backend/vector_service.py:check_duplicate(...)` in admin upload prior to insertion.

#### Phase 2: Add “generation as a service” API (before fine-tuning)
- Add an admin endpoint:
  - `POST /admin/questions/generate`
- Store generated questions as **drafts** in Postgres with status fields.
- Add admin review/approval to publish into the main question bank.

#### Phase 3: Open-source LLM + PEFT
- Inference:
  - Run vLLM or Ollama locally; in production, vLLM is common.
- Fine-tuning:
  - Export accepted questions to JSONL.
  - Train LoRA adapters with PEFT.
  - Load base model + adapter for inference.

#### Phase 4: Semantic cache
- Embed the “generation intent” (topic, constraints).
- Check vector similarity prior to generation to avoid near-duplicate prompts and outputs.

#### Important security note
`backend/synth_data.py` contains a hard-coded API key string. Move it to environment variables immediately if that script is used outside your local machine.

---

## 3) Real-Time Competition (Battle) Module (WebSockets + Redis)

### What the methodology claims
- FastAPI WebSockets for real-time state sync.
- Redis as ephemeral store + leaderboard via sorted sets.

### What is implemented today
- WebSocket battle endpoint exists in `backend/main.py`.
- Battle state and leaderboard are handled **in memory** in `backend/battle_manager.py`.

### What is missing / inaccurate vs methodology
- Redis is not used for battle state.
- In-memory state will not scale beyond one backend instance and is lost on restart.

### How to implement it

#### A. Store battle state in Redis
Suggested keys:
- `battle:{room_code}:state` (JSON document)
- `battle:{room_code}:leaderboard` (sorted set)

Operations:
- `ZINCRBY battle:{room_code}:leaderboard points user_id`
- Use `HSET` or JSON for per-user time/correct counts.

#### B. Multi-instance broadcast
If you run multiple backend instances:
- Use Redis Pub/Sub channels:
  - `battle:{room_code}:events`
- Each instance subscribes and forwards to its local WebSocket connections.

#### C. Persist finals to Postgres
You already have battle tables; keep using them for the final durable record.

---

## 4) Event-Driven Gamification & Rewards Engine (Kafka EDA)

### What the methodology claims
- Kafka broker, producers publish user-action events.
- Independent consumers compute XP/streak/badges.
- Redis/Postgres hybrid.

### What is implemented today
- XP/levels/streaks/badges exist in the monolith:
  - Models in `backend/models.py`
  - Update logic in `backend/ml_service.py`

### What is missing / inaccurate vs methodology
- Kafka is not implemented in code (only referenced in docs).
- No event schema, no producers, no consumers.

### How to implement it (incremental)

#### Step 1: Define events
Create a small set of event payloads:
- `AttemptSubmitted`
- `PracticeCompleted`
- `BattleCompleted`
- `DiscussionVoted`

#### Step 2: Add a message bus
Option A: Kafka (matches methodology)
- Producer in FastAPI endpoints
- Consumer service updates XP/streak/badges

Option B: Celery as stepping stone
- Same payloads, distributed execution, faster to ship

#### Step 3: Split services only if needed
Start with one consumer; split later for scale.

---

## 5) Knowledge Hub & Semantic Search (Hybrid lexical + semantic)

### What the methodology claims
- UGC stored in Postgres, embeddings indexed in Weaviate.
- Hybrid search combines ANN semantic + full-text lexical.

### What is implemented today
- Discussions + votes exist (question-level community feature) in `backend/main.py` and `backend/models.py`.

### What is missing / inaccurate vs methodology
- No hybrid search endpoint.
- No Postgres full-text search (`tsvector`) integration.
- No embedding pipeline for UGC.
- No true “Knowledge Hub” content type with peer review + karma beyond question discussions.

### How to implement it

#### A. Add a KnowledgeContent model
Fields:
- `author_id`, `title`, `body`, `status`, timestamps
- review and karma fields as needed

#### B. Lexical search (Postgres)
- Add a `tsvector` index on `(title || body)`
- Endpoint: `GET /knowledge/search?q=...`

#### C. Semantic search
- Generate embeddings (SentenceTransformers or Weaviate vectorizer)
- Index to Weaviate collection

#### D. Hybrid ranking
Combine lexical rank + semantic similarity (weighted sum) and return a merged set.

---

## 6) Cross-cutting infrastructure gaps

### Current local dev
- `docker-compose.yml` runs backend + frontend only and uses SQLite.

### Needed to fully match methodology
- Postgres service (or managed Postgres)
- Redis service
- Weaviate service (or hosted Weaviate)
- Kafka (and Zookeeper/KRaft)
- Celery worker + Celery beat

---

## Recommended implementation order (highest ROI)
1. **Fix broken wiring** (missing function calls; choose and wire one vector backend).
2. Add **Redis** and migrate caches + battle ephemeral state.
3. Add **Celery + reminders** (email/SMS) and user reminder preferences.
4. Implement **BKT-style mastery probabilities** and update practice selection.
5. Implement **event-driven gamification** (Celery first or Kafka directly).
6. Build the **Knowledge Hub hybrid search** (lexical first, semantic second, hybrid third).
