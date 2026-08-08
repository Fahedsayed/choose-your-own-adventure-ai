# API Request Lifecycle — Story Generation

This document traces the lifecycle of the story generation request end-to-end in this repository. It follows the exact flow from the React UI "Generate Story" button through the FastAPI backend and back into React state/UI.

---

## Files inspected
- frontend/src/components/StoryGenerator.jsx
- frontend/src/components/ThemeInput.jsx
- frontend/src/components/ExampleThemes.jsx
- frontend/src/components/StoryLoader.jsx
- frontend/src/components/LoadingStatus.jsx
- frontend/src/util.js
- backend/routers/story.py
- backend/routers/job.py
- backend/core/story_factory.py
- backend/core/mock_story_generator.py
- backend/models/job.py
- backend/models/story.py
- backend/schemas/job.py
- backend/schemas/story.py
- backend/db/database.py
- backend/core/config.py

---

## 1. Request Overview
Three main API requests are involved in the story generation flow:

- POST `/api/stories/create` — start story generation (returns a job object with `job_id`).
- GET `/api/jobs/{job_id}` — poll this to check status (`pending`, `processing`, `completed`, `failed`).
- GET `/api/stories/{story_id}/complete` — fetch the full generated story and nodes when ready.

These are implemented in `backend/routers/story.py` and `backend/routers/job.py`.

---

## 2. Request #1 — POST `/api/stories/create`

Trigger
- User clicks the "Generate Story" button in the UI (ThemeInput → StoryGenerator).

Frontend component
- `frontend/src/components/ThemeInput.jsx` (input and submit form)
- `frontend/src/components/StoryGenerator.jsx` (parent orchestrating generation)

Event handler
- In `ThemeInput.jsx`, `handleSubmit` prevents default form submission, validates `theme`, and calls the supplied `onSubmit(theme)` prop.

Function that creates the API request
- `StoryGenerator.generateStory(theme)` (in `StoryGenerator.jsx`) is called by `ThemeInput` via `onSubmit`.

HTTP method
- POST

URL requested
- `${API_BASE_URL}/stories/create`
- `API_BASE_URL` is defined in `frontend/src/util.js`. In dev it resolves to `"/api"` (so the request becomes `/api/stories/create`). Vite proxy forwards `/api` to backend (vite.config.js proxies `/api` to http://127.0.0.1:8010).

Request body
- JSON: `{ "theme": "the-chosen-theme" }`

Headers
- Axios default headers. No custom auth headers in code. Browser will send cookies; the backend sets a cookie named `session_id`.

Where response is received
- `const response = await axios.post(`${API_BASE_URL}/stories/create`, {theme})` inside `generateStory`.
- The handler extracts `job_id` and `status` from `response.data`.

Relevant code snippet (frontend)

```js
// StoryGenerator.generateStory
const response = await axios.post(`${API_BASE_URL}/stories/create`, {theme})
const {job_id, status} = response.data
setJobId(job_id)
setJobStatus(status)
pollJobStatus(job_id)
```

Explanation (beginner-friendly)
- The form collects the theme string and calls a function in `StoryGenerator`. That function sends a POST request with `{theme}` to the backend. The backend replies with a job record (including a unique `job_id`). The frontend stores that `job_id` and begins polling the job status endpoint.

---

## 3. Phase 2 — Backend route receiving POST `/api/stories/create`

Router file
- `backend/routers/story.py`

Router prefix
- At top of file: `router = APIRouter(prefix="/stories", tags=["stories"])`. The app mounts this router with `app.include_router(story.router, prefix=settings.API_PREFIX)` in `backend/main.py` — and `settings.API_PREFIX` reads `/api` from `.env`. So the full path becomes `/api/stories`.

HTTP method and endpoint
- Method: POST
- Endpoint: `/api/stories/create` (router prefix `/stories` + route `@router.post("/create")` and app prefix `/api`)

Python function handling request
- `create_story(request: CreateStoryRequest, background_tasks: BackgroundTasks, response: Response, session_id: str = Depends(get_session_id), db: Session = Depends(get_db))`

Request model/schema
- `CreateStoryRequest` defined in `backend/schemas/story.py`:
```py
class CreateStoryRequest(BaseModel):
    theme: str
```

Fields received
- `theme` (string)

Dependencies used
- `session_id` — via `get_session_id` dependency which reads a cookie `session_id` if present or generates a UUID and returns it.
- `db` — provided by `get_db()` dependency that yields a SQLAlchemy session (from `backend/db/database.py`).

Cookies/session
- `create_story` sets a cookie `session_id` on the response: `response.set_cookie(key="session_id", value=session_id, httponly=True)`.
- If the caller already had a `session_id` cookie, that value is used; otherwise a new UUID session id is created.

BackgroundTasks
- The route receives `background_tasks: BackgroundTasks` and uses `background_tasks.add_task(generate_story_task, job_id=..., theme=..., session_id=...)` to schedule the heavy work.

How FastAPI maps the request
- FastAPI matches POST `/api/stories/create` because the application included the router with `prefix=settings.API_PREFIX` (`/api`) and the router defines `prefix="/stories"` and `@router.post("/create")`. The Pydantic model `CreateStoryRequest` validates the JSON body.

---

## 4. Phase 3 — Backend logic after receiving request

What the route does (summary)
- Sets cookie `session_id`.
- Generates a new `job_id` (UUID string) locally.
- Creates a `StoryJob` DB record with `job_id`, `session_id`, `theme`, and `status='pending'`.
- Commits the DB session.
- Registers a background task `generate_story_task(job_id, theme, session_id)`.
- Returns the `job` object.

Database operations
- `db.add(job)` then `db.commit()` — inserts into `story_jobs` with columns in `backend/models/job.py`.

Is a StoryJob created?
- Yes. The code constructs a `StoryJob` instance and stores it in DB. See `backend/models/job.py` for schema.

What is stored in the job?
- `job_id` (UUID string)
- `session_id` (UUID string assigned or passed via cookie)
- `theme` (string)
- `status` (string): set to `"pending"` initially
- `story_id` is null at first
- `created_at` timestamp set by DB default

How job_id is generated
- `job_id = str(uuid.uuid4())` inside `create_story`.

Background task started
- `background_tasks.add_task(generate_story_task, job_id=job_id, theme=request.theme, session_id=session_id)` — this schedules the synchronous function `generate_story_task` to run in background after returning the response.

Which function performs the actual story generation?
- `generate_story_task(job_id, theme, session_id)` defined in `routers/story.py` runs in background and calls `StoryFactory.generate_story(db, session_id, theme)`.

How StoryFactory fits
- `backend/core/story_factory.py` chooses a provider based on `settings.STORY_PROVIDER` (mock or openai) and calls `provider.generate_story(db, session_id, theme)`.

Mock provider behavior
- When `STORY_PROVIDER` is `mock`, `core/mock_story_generator.py::MockStoryGenerator.generate_story()` is called.
- It creates a `Story` record and multiple `StoryNode` records, sets options, commits, and returns the `story_db` object.

Job status updates
- In `generate_story_task`, after locating the job it sets `job.status = 'processing'` and `db.commit()`.
- After `StoryFactory.generate_story` returns, `job.story_id = story.id`, `job.status = 'completed'`, `job.completed_at = datetime.now()`, then `db.commit()`.
- If an exception occurs during generation, `job.status = 'failed'`, `job.completed_at = datetime.now()`, `job.error = str(e)`, and `db.commit()`.

Where story id is stored
- `job.story_id = story.id` is set inside `generate_story_task` after generation completes.

If any behavior unclear
- All these behaviors are present in the inspected code. No guessing required.

---

## 5. Phase 4 — What the POST endpoint returns

What Python object is returned
- The route returns the `job` SQLAlchemy model instance (the same `StoryJob` instance created and committed).

Response model
- `response_model=StoryJobResponse` in the route decorator. `StoryJobResponse` is a Pydantic model mapping attributes from the SQLAlchemy object (via `Config.from_attributes = True`).

JSON the frontend receives
- Example shape (keys found in `schemas.job.StoryJobResponse`):
```json
{
  "job_id": "<uuid>",
  "status": "pending",
  "created_at": "2026-08-08T...",
  "story_id": null,
  "completed_at": null,
  "error": null
}
```

Where `job_id` comes from
- Generated by `str(uuid.uuid4())` in the create route.

What `status` represents
- Current job state: `pending` (immediately after creation), then `processing`, then `completed` or `failed` depending on background work.

Is `story_id` available immediately?
- No. Initially `story_id` is `null` because generation happens in background; it is set later by `generate_story_task` when the story is created.

---

## 6. Phase 5 — Frontend response handling

Where response is received
- `StoryGenerator.generateStory` receives the POST response.

How `job_id` and `status` are stored
- `setJobId(job_id)` and `setJobStatus(status)` (React `useState` hooks in `StoryGenerator.jsx`).

What state changes
- `loading` set earlier to `true`, `theme` set to the value, `jobId` updated, `jobStatus` updated.

`useEffect` logic triggered
- `useEffect` watches `[jobId, jobStatus]`. If `jobId` exists and `jobStatus === 'processing'`, it starts a `setInterval` poll every 5 seconds calling `pollJobStatus(jobId)`.

Does frontend start polling immediately?
- After the POST it calls `pollJobStatus(job_id)` once explicitly, then sets up polling if the job status becomes `processing`.

Which endpoint is polled
- GET `${API_BASE_URL}/jobs/${id}` → `/api/jobs/{job_id}`.

What happens when job completes
- In `pollJobStatus`, on receiving `status === 'completed' && story_id`, it calls `fetchStory(story_id)`.

How frontend obtains final `story_id`
- The polled job endpoint returns `story_id` when background task finishes and updates the DB. The frontend reads `story_id` from that job response.

How React navigates to story page
- `fetchStory` calls `navigate(`/story/${id}`)` (React Router `useNavigate`) which transitions to StoryLoader route.

---

## 7. Phase 6 — Polling lifecycle GET `/api/jobs/{job_id}`

Polling logic (frontend)
- `pollJobStatus(id)` uses axios.get to request `/api/jobs/{id}` and reads `{status, story_id, error}` from response.
- It updates local state with `setJobStatus(status)` and triggers follow-up actions (error handling or fetchStory when completed).

FastAPI route
- `backend/routers/job.py` route `@router.get("/{job_id}", response_model=StoryJobResponse)` handles the GET. It runs `job = db.query(StoryJob).filter(StoryJob.job_id == job_id).first()` and returns the job or 404.

Database lookup
- Simple SQLAlchemy query against `story_jobs` table by `job_id` string.

Job status response
- Same `StoryJobResponse` model as in POST response, containing up-to-date `status` and possibly `story_id` when finished.

React state update
- `setJobStatus(status)` updates job status; on completed + story_id, `fetchStory` is run.

Why polling is necessary
- Generation is performed asynchronously in a background task; the initial POST returns immediately with a job id. The frontend must poll to learn when the background work completes and what `story_id` was produced.

---

## 8. Phase 7 — Final story fetch GET `/api/stories/{story_id}/complete`

What triggers this request
- When the job polling detects `status === 'completed'` and sees a `story_id`, the frontend calls `fetchStory(story_id)` which navigates to `/story/{id}`. The `StoryLoader` component (route) mounts and calls `loadStory(id)`, which triggers the GET request.

Which React component makes it
- `frontend/src/components/StoryLoader.jsx` makes `axios.get(`${API_BASE_URL}/stories/${storyId}/complete`)`.

Which FastAPI route receives it
- `backend/routers/story.py` defines `@router.get("/{story_id}/complete", response_model=CompleteStoryResponse)` which handles the request.

How backend retrieves the story
- `story = db.query(Story).filter(Story.id == story_id).first()` and error if not found.

How StoryNodes are retrieved
- `nodes = db.query(StoryNode).filter(StoryNode.story_id == story.id).all()`

How complete story tree is constructed
- `build_complete_story_tree` converts DB nodes into `CompleteStoryNodeResponse` objects, finds the `root_node` (node with `is_root` True), assembles `all_nodes` dict keyed by node id, and builds `CompleteStoryResponse` with `root_node` and `all_nodes`.

Response model returned
- `CompleteStoryResponse` (see `backend/schemas/story.py`) — contains `id`, `title`, `session_id`, `created_at`, `root_node` and `all_nodes`.

How React uses the response
- `StoryLoader` sets `setStory(response.data)` and renders `<StoryGame story={story} />`.

How `StoryGame` displays story
- `StoryGame` (inspected earlier) receives the `story` object and renders content and choice buttons; clicking choices navigates or fetches next node according to app logic.

---

## 9. Complete Request Lifecycle Diagram (adapted to code)

User
 ↓
Click "Generate Story" (ThemeInput form submit)
 ↓
`ThemeInput.handleSubmit` -> `onSubmit(theme)` (prop)
 ↓
`StoryGenerator.generateStory(theme)`
 ↓
POST `/api/stories/create` (axios) → Vite dev server `/api` proxy → FastAPI
 ↓
`backend.routers.story.create_story` receives request
 ↓
Create `StoryJob` (status: pending) in DB; set cookie `session_id`
 ↓
Return job object JSON (contains `job_id`)
 ↓
Frontend saves `job_id`, `status`; starts polling via `pollJobStatus`
 ↓
GET `/api/jobs/{job_id}` repeated until completed
 ↓
`backend.routers.job.get_job_status` reads job row and returns status (and `story_id` when available)
 ↓
When job shows `completed` and has `story_id`: frontend calls `navigate(/story/{story_id})`
 ↓
`StoryLoader` loads `/api/stories/{story_id}/complete`
 ↓
`backend.routers.story.get_complete_story` builds `CompleteStoryResponse` from `stories` and `story_nodes`
 ↓
Frontend receives story JSON, `setStory(...)`, `StoryGame` renders story and choices
 ↓
UI updates show generated story and options

---

## 10. Key Concepts Learned (concise, relevant)

- HTTP request: message sent from client (browser) to server (FastAPI) to perform an action or get data.
- HTTP method: describes the action (POST to create/start, GET to read).
- URL: endpoint address (e.g., `/api/stories/create`).
- Request body: JSON sent with POST; here `{theme}`.
- API endpoint / FastAPI route: Python function decorated to handle requests (e.g., `@router.post("/create")`).
- Pydantic request model: `CreateStoryRequest` validates incoming JSON.
- Response model: Pydantic model (e.g., `StoryJobResponse`) defines the JSON the API returns.
- JSON: serialized data exchange format between frontend and backend.
- Database operation: SQLAlchemy session writes/reads rows (e.g., inserting StoryJob, Story, StoryNode).
- Background task: FastAPI `BackgroundTasks` schedules work after responding so the request returns quickly.
- Polling: frontend periodically requests job status to know when background work finishes.
- React state: `useState` stores `jobId`, `jobStatus`, and `story`.
- `useEffect`: used to start/stop polling based on state changes.
- API response handling: frontend reads `response.data` and updates state accordingly.

---

## 11. Questions You Should Be Able to Answer (answers)

1. What triggers the story creation API request?
   - Submitting the ThemeInput form (user clicks "Generate Story").

2. Where is the frontend request created?
   - `StoryGenerator.generateStory(theme)` via `axios.post(`${API_BASE_URL}/stories/create`, {theme})`.

3. What data is sent?
   - `{ "theme": "<theme string>" }`.

4. Which FastAPI endpoint receives it?
   - POST `/api/stories/create` (mounted via router prefix `/stories` and app prefix `/api`).

5. Which Python function handles it?
   - `create_story` in `backend/routers/story.py`.

6. What happens in the database?
   - A new `StoryJob` row is inserted with `job_id`, `session_id`, `theme`, `status='pending'`.

7. Why is a background task used?
   - Story generation can be long-running; background task allows immediate response while generation happens asynchronously.

8. What does the backend return?
   - The `StoryJob` info serialized to JSON via `StoryJobResponse` (includes `job_id`, `status`, timestamps, nullable `story_id`).

9. Where does `job_id` come from?
   - Generated in `create_story` using `str(uuid.uuid4())`.

10. Why does the frontend poll the job endpoint?
    - To learn when the background generation completes and to get the produced `story_id`.

11. How does the frontend know when generation is complete?
    - The polled `/api/jobs/{job_id}` endpoint returns `status: 'completed'` and `story_id`.

12. How does it get the final `story_id`?
    - From the JSON body of `GET /api/jobs/{job_id}` once the background task sets `job.story_id` and commits.

13. Which request loads the completed story?
    - GET `/api/stories/{story_id}/complete` (initiated by `StoryLoader` when navigating to `/story/{id}`).

14. How does the response become React state?
    - `StoryLoader.loadStory` does `setStory(response.data)`.

15. How does that state eventually become UI?
    - `StoryLoader` renders `<StoryGame story={story} />`, and `StoryGame` renders content and choices into HTML.

---

## 12. Observations / Possible Improvements (documented only — no code changes)

- The linter warns about a missing `useEffect` dependency for `pollJobStatus` in `StoryGenerator.jsx`. This is a warning (react-hooks/exhaustive-deps) but not a runtime error. It may be acceptable here, but it is a potential source of stale closures; consider wrapping `pollJobStatus` with `useCallback` or declaring it inside the effect if refactoring is allowed.

- The Vite `server.proxy` forwards `/api` to `http://127.0.0.1:8010` which is fine for dev. Ensure production config points to correct backend.

- Session cookie `session_id` is set httponly; frontend cannot read it which is OK for session identification.

---

## 13. What I documented and what changed

- Document created: `docs/api-request-lifecycle.md` (this file).
- No application code was modified.

---

If you want, I can now:
- Open this file in the editor for review, or
- Walk through a live request with logs (I can re-run a generation while tailing backend logs) to show a step-by-step timeline with timestamps.

Tell me which you'd prefer next.