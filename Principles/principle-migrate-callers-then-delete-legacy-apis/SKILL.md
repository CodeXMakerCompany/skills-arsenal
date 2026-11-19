---
name: principle-migrate-callers-then-delete-legacy-apis
description: Apply when introducing a new internal API while old callers still exist. Migrate callers and delete the old API in the same wave instead of preserving compatibility layers.
---

# Migrate Callers Then Delete Legacy APIs

One wave: add the new API, move every caller, delete the old one. A compatibility layer that survives the PR becomes permanent, and then the codebase has two ways to do one thing and an agent copying the nearest example picks the wrong one half the time.

- **Update the tests to assert the new contract**, and delete tests that only protected pre-refactor implementation details.
- **Delete the old path's dead code** in the same change: the unused branch, the feature flag that is now always one value, the adapter nobody calls.
- **Leave no stub.** A re-export that forwards to the new name is a compatibility layer with better branding.

**When this applies:**

- No external consumer depends on backward compatibility.
- The project can absorb a coordinated breaking change.
- The new API is part of a simplification, not a parallel universe.

**When it does not:** a public API, a published package, a mobile client you cannot force to update, or a service whose consumers deploy on their own schedule. There, version deliberately, publish the deprecation window with a date, and track who is still on the old path. Say who the external consumer is. "Someone might depend on it" is not a consumer.
