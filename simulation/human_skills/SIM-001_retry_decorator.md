---
name: retry-decorator
description: Implement a retry decorator with exponential backoff for Python functions.
task_id: SIM-001
author: human-expert
authoring_time_minutes: 45
iterations: 3
---

# Skill: Retry Decorator with Exponential Backoff

## Trigger Condition
When a task requires implementing retry logic with configurable backoff for function calls that may fail transiently.

## Strategy

### Step 1: Define the Decorator Interface
- Accept parameters: `max_retries` (int), `base_delay` (float, seconds), `max_delay` (float, seconds), `retryable_exceptions` (tuple of exception types)
- Use `functools.wraps` to preserve the wrapped function's metadata

### Step 2: Implement the Backoff Logic
- Calculate delay as: `min(base_delay * (2 ** attempt), max_delay)`
- Add jitter: `delay * (0.5 + random.random() * 0.5)` to prevent thundering herd
- Use `time.sleep(delay)` between retries

### Step 3: Implement Logging
- Log each retry with: attempt number, exception type, exception message, delay before next retry, remaining retries
- Use Python's `logging` module at WARNING level for retries, ERROR for final failure

### Step 4: Handle Edge Cases
- If `max_retries` is 0, execute once without retry
- If the exception is NOT in `retryable_exceptions`, re-raise immediately
- If all retries exhausted, re-raise the last exception

### Step 5: Validate
- Test with a function that fails N times then succeeds
- Test with a non-retryable exception (should raise immediately)
- Test that delay increases exponentially
- Test that `max_delay` caps the backoff

## Common Pitfalls
- Forgetting `functools.wraps` causes debugging issues
- Not capping the delay leads to unreasonably long waits
- Retrying on ALL exceptions (including KeyboardInterrupt) is dangerous
- Not adding jitter causes synchronized retry storms
