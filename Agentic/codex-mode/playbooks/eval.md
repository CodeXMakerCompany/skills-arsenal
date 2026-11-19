# Eval

**You own the experiment design. Plan, blind, run, synthesize.** For comparing prompts, models, retrieval strategies, or agent designs.

**Non-negotiables for blinding.** The grader never sees which arm produced an output. Arm labels are opaque (`arm-a`, `arm-b`), order is shuffled per item, and the author of an arm never grades it. An unblinded eval measures your hope.

1. **Write the decision the eval settles** and the result that would change it. "We adopt arm B if it beats A by more than the run-to-run spread on the 120-item set." No decision, no eval.
2. **Build the set before the arms.** Real traffic beats synthetic. Hold out a test slice you score every round and never tune against, plus a train slice you may look at freely. Route set construction through **llm-evals**.
3. **Fix the grader first.** A rubric with independently gradeable criteria, a deterministic checker where the answer is checkable, or a model judge on a different model family than any arm. Measure the grader against human labels on a sample before you trust it.
4. **One variable per arm.** An arm that changes the prompt and the model answers nothing.
5. **Run with the cost written down.** Count items times arms times trials times tokens before you spend, and say the number. Batch where latency does not matter: it is half price.
6. **Report the spread, not just the mean.** At least three trials per arm. A gap smaller than the run-to-run spread is no difference, and saying so is a valid result.
7. **Vet every number** with **benchmark-checklist** questions 4 and 7: did any run error, and did the work actually happen.
8. **Record it** so the next round starts from the measurement, not from memory. Keep the set, the grader, the per-item scores, and the command that reruns it.
