# Testing

## Testing framework

- Backend tests use Python's built-in `unittest` framework.
- Frontend currently does not have a dedicated test runner configured in the repository.

## Test commands

Backend tests:

```bash
./.venv/Scripts/python.exe -m unittest discover -s backend/tests -p "test_*.py"
```

Frontend build check:

```bash
npm run build
```

## Existing test locations

- Backend tests: [backend/tests](../backend/tests)
- Frontend: no current frontend test files or test runner configuration were found.

## Representative backend test

Example: [backend/tests/test_job_endpoint.py](../backend/tests/test_job_endpoint.py)

- Arrange: create an in-memory SQLAlchemy session and insert a `StoryJob` row.
- Act: call `get_job_status(job_id="job-123", db=self.session)`.
- Assert: verify the returned response contains the expected job id, theme, and status.

This verifies that the job-status lookup returns the correct data for an existing job.

## Representative request-model test

Example: [backend/tests/test_story_request_model.py](../backend/tests/test_story_request_model.py)

- Arrange: create a `CreateStoryRequest` with a theme string.
- Act: instantiate the Pydantic model.
- Assert: verify valid input is accepted and blank input raises a validation error.

This verifies the request validation behavior for the story-creation endpoint input.

## Frontend test availability

- No frontend test files are currently present.
- The frontend package includes a build script, but not a test script.

## Current testing gap

A meaningful untested behavior is the full story-creation route flow:

- the request is accepted,
- a `StoryJob` is persisted,
- and the background task path is triggered.

This is not covered by the existing tests, so the current suite verifies model and lookup behavior, but not the end-to-end route behavior.

## Test results

The backend tests were executed successfully:

- Command used: `./.venv/Scripts/python.exe -m unittest discover -s backend/tests -p "test_*.py"`
- Result: 4 tests ran, all passed.
