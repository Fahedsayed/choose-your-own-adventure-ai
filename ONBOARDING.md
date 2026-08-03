## Here is a comprehensive, production-grade ONBOARDING.md file tailored specifically to your exact codebase architecture. You can place this file directly in your repository root to guide new developers through their first day.

## 🗺️ Developer Onboarding Guide: Architecture & Data Flow

## Welcome to the team! This guide breaks down the core architecture of our React + Vite interactive story platform. Our system uses a route-driven, state-encapsulated design with explicit boundaries between story generation and runtime playback.

## 🚀 Architectural Overview

Our frontend is split into two primary workflows managed dynamically by React Router DOM:

1.  Story Generation Flow (/): Collects user themes, handles asynchronous backend jobs, and tracks operational progress.
2.  Story Playback Flow (/story/:id): Loads the complete story graph data and handles the interactive playthrough logic.

## Refer to the system architecture diagram in our documentation (/docs/architecture-diagram.png) to see how components, state hooks, and backend endpoints connect.

## 📁 Core Component Hierarchy & State Layout## 1. Root & Routing (App.jsx)

- Role: The entry point wrapper of our React application.
- Composition: Renders BrowserRouter → Routes.
- Routing Table:
- Route path="/": Renders <StoryGenerator />
  - Route path="/story/:id": Renders <StoryLoader />

## 2. Story Generation (StoryGenerator.jsx)

- Location: src/components/StoryGenerator.jsx
- Local State Managed:
- theme (string): The current user-defined text prompt.
  - jobId (string/null): The active asynchronous job tracking ID.
  - jobStatus (string): Status of generation ('idle', 'pending', or 'completed').
  - loading (boolean): Flag to toggle background spinners.
  - error (string/null): Captures and displays backend communication faults.
- Conditional UI Composition:
- Renders <ThemeInput /> only when jobStatus === 'idle'.
  - Renders <LoadingStatus /> only when loading === true.

## 3. Story Playback System## <StoryLoader />

- Role: Data-fetching boundary for individual story profiles.
- Local State Managed: story, loading, error.
- Composition: Once story data is successfully fetched, it composes <StoryGame /> and passes the full story object down via Props.

## <StoryGame />

- Role: Handles interactive playthrough state and local node navigation.
- Local State Managed:
- currentNodeId (string): The current node index of the story tree.
  - currentNode (object): Raw node text and child choice configurations.
  - options (array): Array of choices presented to the user.
  - isEnding (boolean): Flags if the current node terminates the story.
  - isWinningEnding (boolean): Distinguishes standard endings from success conditions.

---

## 🔄 End-to-End Data Flow Lifecycles

New developers should trace these two critical data paths when exploring the codebase:

## Lifecycle A: Story Generation & Job Polling

1.  User Submission: The user enters a string inside <ThemeInput />. It bubbles up to <StoryGenerator /> via a submission callback.
2.  Job Initiation: StoryGenerator updates loading and sends an HTTP request:
    $$\text{POST} \longrightarrow \texttt{/stories/create} \quad \{\text{body}: \text{theme}\}$$
3.  Receipt: The backend responds immediately with a unique job ID and an initial state: { jobId: "xyz-123", jobStatus: "pending" }.
4.  The Polling Loop: A useEffect hook inside StoryGenerator runs an interval loop to query the worker status:
    $$\text{GET} \longrightarrow \texttt{/jobs/:id}$$
5.  Route Transition: Once the job response returns jobStatus: "completed", it also provides a storyId. StoryGenerator calls navigate('/story/' + storyId) to hand off control to the playback router.

## Lifecycle B: Interactive Playback & Game Loop

1.  Data Hydration: <StoryLoader /> mounts at /story/:id. A useEffect hook reads the URL parameter and executes the final data fetch:
    $$\text{GET} \longrightarrow \texttt{/stories/:id/complete}$$
2.  Prop Injection: The API returns the complete story graph. StoryLoader renders <StoryGame story={storyData} />.
3.  The Local Mutation Loop: When a user selects a choice link on-screen, an internal state handler fires. This changes currentNodeId, driving an internal re-render that re-calculates options, isEnding, and isWinningEnding entirely in local client memory without secondary network requests.

---

## 🛠️ Onboarding Development Checklist

To get your local workspace matching production behavior, complete these steps:

- Copy .env.example to .env.local and confirm your backend endpoint port targets match.
- Run npm install followed by npm run dev to boot up the Vite bundler.
- Open the project in your IDE and trace a mock generation from ThemeInput.jsx down through StoryGenerator.jsx to see the state updates fire in real-time using React DevTools.
- Run npm run test to verify your environment passes all initial suite checks.

---

If you want to append more technical depth to this file, we can:

- Add a Directory Structure Map section linking components to physical file paths
- Add a Common Commands / Scripts table for testing and building
