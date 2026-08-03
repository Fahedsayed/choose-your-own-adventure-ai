Frontend Architecture

## Routing Structure

```
App (with BrowserRouter)
├── Route: / → StoryGenerator
└── Route: /story/:id → StoryLoader
```

## Component Hierarchy & Data Flow

### Path 1: Story Generation (`/`)

```
App (Router wrapper)
  └── StoryGenerator (manages story creation & polling)
      ├── ThemeInput (form input)
      ├── LoadingStatus (shows loading spinner)
      └── useNavigate() → navigate to /story/{story_id}
```

**StoryGenerator Flow:**

1. User enters theme → ThemeInput.onSubmit()
2. generateStory() makes POST to `/stories/create`
3. Receives `job_id` and initial `status`
4. useEffect sets up polling interval (every 5s)
5. pollJobStatus() polls `/jobs/{job_id}` until completed
6. On completion, navigates to `/story/{story_id}`

**State in StoryGenerator:**

- `theme` - user input
- `jobId` - job ID for polling
- `jobStatus` - "processing", "completed", "failed"
- `loading` - show LoadingStatus
- `error` - error messages

### Path 2: Story Playing (`/story/:id`)

```
App (Router wrapper)
  └── StoryLoader (fetches story, manages navigation)
      ├── useParams() → extract story {id}
      ├── LoadingStatus (loading state)
      ├── Error message (if story not found)
      └── StoryGame (interactive story UI)
          ├── currentNodeId (which story node to display)
          ├── currentNode (content, options, ending status)
          ├── options (choices available to user)
          └── chooseOption() → update currentNodeId
```

**StoryLoader Flow:**

1. Extract `id` from URL via useParams()
2. useEffect triggers loadStory() on mount
3. GET `/stories/{id}/complete` fetches full story structure
4. Pass story to StoryGame

**State in StoryLoader:**

- `story` - complete story object with all nodes
- `loading` - fetch status
- `error` - "Story not found" or other errors

**StoryGame Flow:**

1. Receives `story` prop from StoryLoader
2. Initialize currentNodeId to root_node.id
3. When user clicks option button → chooseOption(option.node_id)
4. currentNodeId update triggers lookup in story.all_nodes
5. Display new node content and options
6. If node.is_ending = true → show ending message

**State in StoryGame:**

- `currentNodeId` - which story node to show
- `currentNode` - current node object from story.all_nodes
- `options` - node.options array
- `isEnding` - whether current node is an ending
- `isWinningEnding` - whether it's a winning vs losing ending

## API Endpoints Used

| Endpoint                 | Method | Component      | Purpose                         |
| ------------------------ | ------ | -------------- | ------------------------------- |
| `/stories/create`        | POST   | StoryGenerator | Create new story generation job |
| `/jobs/{id}`             | GET    | StoryGenerator | Poll job status (5s intervals)  |
| `/stories/{id}/complete` | GET    | StoryLoader    | Fetch complete story data       |

## Key Hooks Used

| Hook            | Component                              | Purpose                                          |
| --------------- | -------------------------------------- | ------------------------------------------------ |
| `useParams()`   | StoryLoader                            | Extract story ID from URL                        |
| `useNavigate()` | StoryGenerator, StoryLoader            | Navigate between routes                          |
| `useState()`    | All components                         | Manage local state                               |
| `useEffect()`   | StoryGenerator, StoryLoader, StoryGame | Side effects (polling, fetching, initialization) |

## Reusable Components

| Component         | Props                 | Purpose                                  |
| ----------------- | --------------------- | ---------------------------------------- |
| **ThemeInput**    | `onSubmit(theme)`     | Form for entering story theme            |
| **LoadingStatus** | `theme`               | Shows loading spinner with theme context |
| **StoryGame**     | `story`, `onNewStory` | Interactive story display with choices   |

## State Management Summary

**Where state lives:**

- Route-level navigation state: App (via Router)
- Story generation state: StoryGenerator (theme, jobId, jobStatus, loading, error)
- Story fetching state: StoryLoader (story, loading, error)
- Story gameplay state: StoryGame (currentNodeId, currentNode, options, ending flags)

**How state changes:**

1. User actions (form submit, button clicks)
2. useState setters
3. useEffect side effects (polling, data fetching)
4. Route navigation (useNavigate)

**Data flow:**

```
User Input
    ↓
Event Handler (onClick, onSubmit)
    ↓
setState
    ↓
Component Re-render
    ↓
[If async] API Call
    ↓
Response → setState
    ↓
Component Re-render
    ↓
UI Updates
```

StoryLoader > StoryGame , LoadingStatus

StoryGenerator > LoadingStatus , ThemeInput
