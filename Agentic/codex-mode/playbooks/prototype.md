# Prototype

**You own the design decision, not the code. The prototype is a throwaway instrument.** The real build follows Feature.

The one playbook where the Laziness Protocol's "smallest change" and the verification bar invert. Speed over polish. Code quality does not matter. No planning.

1. **State the fork the prototype settles**, in one sentence, with the observation that decides it. A prototype that settles nothing is procrastination with a dev server running.
2. **Build the cheapest thing that produces that observation.** Hardcode, fake the auth, inline the data, skip the error states. One file is fine.
3. **Build two or three variants where feel decides** (principle-exhaust-the-design-space), and put them side by side. Propose a variation the user did not ask for. Throw an approach away and try another.
4. **Observe, do not argue.** Record what each variant actually did: the latency, the output quality, the token count, the cost, the screenshot.
5. **Recommend with the observation attached.** Settle by run whatever a run can settle, and leave only product and preference calls to the human.
6. **Throw it away.** The prototype does not get merged, hardened, or quietly promoted into production. Say in the handoff that it is throwaway and name what the real build must do that the prototype faked.
