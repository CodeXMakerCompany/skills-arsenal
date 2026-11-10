---
name: state-machine-architect
description: Finite State Machine (FSM) design and implementation. Use when modeling deterministic phases or modes - game flow, combat turns, AI behavior, UI screens, workflows, connection or order lifecycles - in any language (TypeScript, Python, C++, C#). Covers when to use an FSM, transition tables, async-safe transitions, and testing.
---

# Finite State Machine Architecture

## When to use (and when not)

Use an FSM when the system:
- is in exactly one of a small, named set of modes at a time,
- has rules about which mode can follow which,
- runs different behavior per mode (enter, update, exit).

Do not use it when:
- states are combinable flags (poisoned AND burning AND stunned): use independent flags or parallel machines.
- behavior is a priority-based decision (AI choosing among options): consider behavior trees or utility AI, optionally with an FSM for the action layer.
- there are only two states and no side effects: a boolean is enough.

Scale options when a flat FSM grows past ~8 states or sprouts duplicate transitions:
- **Hierarchical (HFSM):** parent states hold shared behavior and transitions (e.g. `Grounded` > `Idle`, `Walking`, `Crouching`).
- **Parallel machines:** one machine per independent axis (movement, weapon, status).
- **Pushdown stack:** push a temporary state (pause, stun), pop to return.

## Design steps

1. List states as nouns or conditions, not actions (`Reloading`, not `Reload`).
2. List events/triggers that cause transitions (input, timer, message, result).
3. Write the transition table before code. Every cell is allowed or forbidden on purpose.
4. Decide what runs on enter, on exit, and per update. Exit undoes what enter set up.
5. Define the initial state and what happens on invalid transition (reject and log; never silently ignore in dev).

Example table:

| From \ To | Idle | Running | Paused | GameOver |
|-----------|------|---------|--------|----------|
| Idle | - | yes | no | no |
| Running | yes | - | yes | yes |
| Paused | no | yes | - | yes |
| GameOver | yes | no | no | - |

## Reference implementation (TypeScript)

Improvements over a naive version: allowed transitions are declared in one table, async hooks cannot interleave (transitions are serialized), `update` is skipped mid-transition, and hooks get the previous or next state name.

```typescript
export interface IState<TContext> {
  readonly name: string;
  onEnter?(context: TContext, from: string | null): void | Promise<void>;
  onUpdate?(context: TContext, deltaTime: number): void;
  onExit?(context: TContext, to: string): void | Promise<void>;
}

/** Map of state name -> names it may transition to. */
export type TransitionTable = Readonly<Record<string, readonly string[]>>;

export class StateMachine<TContext> {
  private current: IState<TContext> | null = null;
  private readonly states = new Map<string, IState<TContext>>();
  private queue: Promise<unknown> = Promise.resolve();
  private transitioning = false;

  constructor(
    private readonly context: TContext,
    private readonly transitions: TransitionTable,
    private readonly onRejected: (from: string | null, to: string, reason: string) => void = () => {},
  ) {}

  registerState(state: IState<TContext>): this {
    if (this.states.has(state.name)) {
      throw new Error(`StateMachine: duplicate state '${state.name}'.`);
    }
    this.states.set(state.name, state);
    return this;
  }

  /** Queues the transition; calls are executed one at a time, in order. */
  transitionTo(name: string): Promise<boolean> {
    const run = this.queue.then(() => this.performTransition(name));
    this.queue = run.catch(() => undefined); // keep the chain alive after a failed hook
    return run;
  }

  update(deltaTime: number): void {
    if (this.transitioning) return;
    this.current?.onUpdate?.(this.context, deltaTime);
  }

  get currentStateName(): string | null {
    return this.current?.name ?? null;
  }

  private async performTransition(name: string): Promise<boolean> {
    const target = this.states.get(name);
    const from = this.current?.name ?? null;

    if (!target) {
      this.onRejected(from, name, "unknown state");
      return false;
    }
    if (this.current && !(this.transitions[this.current.name] ?? []).includes(name)) {
      this.onRejected(from, name, "transition not allowed");
      return false;
    }

    this.transitioning = true;
    try {
      await this.current?.onExit?.(this.context, name);
      this.current = target;
      await target.onEnter?.(this.context, from);
      return true;
    } finally {
      this.transitioning = false;
    }
  }
}
```

Usage:

```typescript
const transitions = {
  Idle: ["Running"],
  Running: ["Idle", "Paused", "GameOver"],
  Paused: ["Running", "GameOver"],
  GameOver: ["Idle"],
} as const;

const fsm = new StateMachine(gameContext, transitions, (from, to, why) =>
  console.warn(`FSM rejected ${from} -> ${to}: ${why}`),
);
fsm.registerState(idleState).registerState(runningState); // ...
await fsm.transitionTo("Idle"); // first call sets the initial state; no source check
```

If all hooks are synchronous (typical in game loops), drop the queue and Promises for a plain synchronous version; keep the same table and rules.

## Language notes

- **C++ / Unreal:** states as `UObject` subclasses or lightweight structs with an enum; keep the current state in a `UPROPERTY` replicated with `OnRep` if networked. Do not run async work in hooks; use timers or delegates and transition on completion.
- **C# / Unity:** enum plus `switch` is fine for under ~6 states; move to state classes once hooks grow. Avoid coroutines that outlive their state; cancel them in `OnExit`.
- **Python:** `Enum` for names, a dict for the table. For workflows consider the `transitions` library instead of hand rolling.
- **UI:** one machine per screen flow; states map to routes or modes, and the table is the navigation contract.

## Core principles

1. **Explicit transitions.** Valid moves live in one table, not scattered `if`s in hooks.
2. **Single entry point.** State changes only through `transitionTo`. No public setter, no direct field writes.
3. **Context injection.** Hooks receive the context; states do not reach for global singletons. This is what makes them testable.
4. **Symmetric hooks.** Whatever `onEnter` starts (timers, listeners, animations, input maps), `onExit` stops.
5. **Small hooks.** A state delegates to services in the context; it does not own game rules.
6. **Re-entrancy safe.** A hook may request a transition, but it is queued, never run inside the current one.
7. **Observable.** Log every accepted and rejected transition in development. A transition history ring buffer makes bugs reproducible.

## Anti-patterns

| Smell | Fix |
|-------|-----|
| `if (state === ...)` checks across many files | Move the behavior into the state, or expose a query on the machine |
| Boolean flags next to the state (`isPausedWhileRunning`) | Add a state or a parallel machine |
| State explosion from combining axes | Split into parallel machines |
| Transition called from inside `onExit` | Queue it; exit must finish first |
| Self-transition meaning "restart" | Make it explicit (`Restart` state or `reset()`), do not rely on a no-op |
| States holding data that outlives them | Put the data on the context |

## Testing

- Table test: for every (from, to) pair, assert allowed or rejected matches the design table.
- Hook symmetry test: after enter then exit, context equals its initial value.
- Sequence test: drive a scripted event sequence and assert the visited state names.
- Async test: fire two `transitionTo` calls without awaiting and assert hooks ran in order, not interleaved.
