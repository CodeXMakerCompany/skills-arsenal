---
name: drag-drop-raycaster
description: Screen-to-world cursor projection, ray-plane intersection, smooth follow interpolation and slot snapping for 3D drag-and-drop. Use when building draggable objects, card/piece/inventory placement on a board, grid or slot snapping, or any mechanic that maps a 2D pointer to a 3D position, in Three.js/TypeScript, Unreal Engine C++/Blueprint, Unity or custom engines.
---

# 3D Drag & Drop: Raycast, Plane, Follow, Snap

A drag is four steps per frame: pointer to ray, ray to point on a plane, point to target position (offset and snap), target to smoothed object position. Keep each step a small pure function so it can be tested without an engine.

## Before you start

1. Identify the engine and camera type (perspective or orthographic). Orthographic rays are parallel, so the ray origin moves with the pointer and the direction is constant. The math below still holds.
2. Decide the drag surface: a horizontal plane (board, table, floor), a camera-facing plane (free 3D move), or the actual geometry under the cursor (surface-following).
3. Decide what can be dropped where (slots, grid cells, free placement) and what happens on an invalid drop (return to origin, stay, destroy).

## Math

Ray: `P(t) = O + D * t`, with `D` normalized.
Plane: point `P0`, normal `N`.

```
denom = dot(D, N)
if |denom| < eps  -> ray parallel to plane, no hit
t = dot(P0 - O, N) / denom
if t < 0          -> plane is behind the ray origin, no hit
hit = O + D * t
```

Special case, horizontal plane at height `h` (Y-up): `t = (h - O.y) / D.y`. In Z-up engines (Unreal) use `Z`.

Choosing the plane:

| Goal | Plane point | Normal |
|------|-------------|--------|
| Slide on table/board | Hit point on the board at drag start | Board up |
| Free 3D move at constant depth | Object position at drag start | Camera forward (negated) |
| Wall-mounted items | Hit point on the wall | Wall normal |

Compute the plane once at drag start and reuse it. Re-deriving it every frame from the lifted object makes the object chase itself.

## TypeScript reference (engine-agnostic)

```typescript
export interface Vec3 { x: number; y: number; z: number }
export interface Ray { origin: Vec3; direction: Vec3 } // direction normalized

const EPS = 1e-6;
const dot = (a: Vec3, b: Vec3) => a.x * b.x + a.y * b.y + a.z * b.z;
const sub = (a: Vec3, b: Vec3): Vec3 => ({ x: a.x - b.x, y: a.y - b.y, z: a.z - b.z });
const addScaled = (o: Vec3, d: Vec3, t: number): Vec3 => ({
  x: o.x + d.x * t, y: o.y + d.y * t, z: o.z + d.z * t,
});

/** General ray-plane intersection. Returns null if parallel or behind the origin. */
export function intersectPlane(ray: Ray, planePoint: Vec3, planeNormal: Vec3): Vec3 | null {
  const denom = dot(ray.direction, planeNormal);
  if (Math.abs(denom) < EPS) return null;
  const t = dot(sub(planePoint, ray.origin), planeNormal) / denom;
  if (t < 0) return null;
  return addScaled(ray.origin, ray.direction, t);
}

/** Horizontal plane shortcut (Y-up). */
export function intersectHorizontalPlane(ray: Ray, planeY: number): Vec3 | null {
  if (Math.abs(ray.direction.y) < EPS) return null;
  const t = (planeY - ray.origin.y) / ray.direction.y;
  if (t < 0) return null;
  return { x: ray.origin.x + ray.direction.x * t, y: planeY, z: ray.origin.z + ray.direction.z * t };
}

/** Frame-rate independent exponential smoothing. speed ~ 10-25. */
export function damp(current: number, target: number, speed: number, dt: number): number {
  return target + (current - target) * Math.exp(-speed * dt);
}

export interface Slot { id: string; center: Vec3; occupied?: boolean }

/** Nearest free slot within radius, measured on the drag plane. Null if none. */
export function findSnapSlot(point: Vec3, slots: readonly Slot[], radius: number): Slot | null {
  let best: Slot | null = null;
  let bestD2 = radius * radius;
  for (const s of slots) {
    if (s.occupied) continue;
    const dx = s.center.x - point.x;
    const dz = s.center.z - point.z; // plane distance; ignore height
    const d2 = dx * dx + dz * dz;
    if (d2 <= bestD2) { bestD2 = d2; best = s; }
  }
  return best;
}
```

### Three.js wiring

```typescript
import * as THREE from "three";

const raycaster = new THREE.Raycaster();
const ndc = new THREE.Vector2();
const plane = new THREE.Plane();
const hit = new THREE.Vector3();
let grabOffset = new THREE.Vector3();

function setPointer(e: PointerEvent, canvas: HTMLCanvasElement) {
  const r = canvas.getBoundingClientRect();           // use the canvas rect, not the window
  ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  raycaster.setFromCamera(ndc, camera);
}

function onPointerDown(e: PointerEvent) {
  setPointer(e, canvas);
  const picked = raycaster.intersectObjects(draggables, false)[0];
  if (!picked) return;
  dragged = picked.object;
  plane.setFromNormalAndCoplanarPoint(new THREE.Vector3(0, 1, 0), picked.point);
  grabOffset.copy(dragged.position).sub(picked.point);  // keeps the grab point under the cursor
  canvas.setPointerCapture(e.pointerId);
}

function onPointerMove(e: PointerEvent) {
  if (!dragged) return;
  setPointer(e, canvas);
  if (raycaster.ray.intersectPlane(plane, hit)) {
    dragTarget.copy(hit).add(grabOffset);
    dragTarget.y += HOVER_HEIGHT;                       // lift for clearance
  }
}

// each frame
dragged.position.x = damp(dragged.position.x, dragTarget.x, 18, dt);
dragged.position.y = damp(dragged.position.y, dragTarget.y, 18, dt);
dragged.position.z = damp(dragged.position.z, dragTarget.z, 18, dt);
```

## Unreal Engine C++

```cpp
// Deprojects the cursor and intersects with an arbitrary plane.
bool GetCursorPlaneIntersection(const APlayerController* PC,
                                const FPlane& Plane,
                                FVector& OutPoint)
{
    if (!PC) return false;

    FVector Origin, Direction;
    if (!PC->DeprojectMousePositionToWorld(Origin, Direction)) return false;

    const float Denom = FVector::DotProduct(Direction, Plane.GetNormal());
    if (FMath::IsNearlyZero(Denom)) return false;       // parallel

    const float T = (Plane.W - FVector::DotProduct(Origin, Plane.GetNormal())) / Denom;
    if (T < 0.f) return false;                          // behind the camera

    OutPoint = Origin + Direction * T;
    return true;
}
```

Notes:
- Equivalent built-in: `FMath::LinePlaneIntersection(Origin, Origin + Direction * Far, Plane)`.
- Plane from a point and normal: `FPlane(PlanePoint, PlaneNormal)`. Create it at drag start.
- Smoothing: `FMath::VInterpTo(Current, Target, DeltaTime, Speed)` is already delta-time based. Use `Speed` 15 to 20.
- Picking: `GetHitResultUnderCursorByChannel` with a dedicated "Draggable" trace channel, not `Visibility`.
- Blueprint: expose the helper as `BlueprintPure` or `BlueprintCallable` in a function library.
- Touch: use `DeprojectScreenPositionToWorld` with the touch location.

## Feel

- **Hover lift:** raise the object along the up axis at drag start (a few cm or a fraction of its height) so it clears collision and reads as "picked up". Animate the lift, do not pop it.
- **Grab offset:** preserve where on the object the user grabbed, as in the wiring above, or the object jumps to center on the cursor.
- **Follow speed:** damping speed 15 to 20 is crisp; lower (8 to 12) for heavy objects. Always use dt-aware smoothing; a bare `lerp(a, b, 0.2)` changes feel with frame rate.
- **Snap:** when a free slot is within radius `R`, set the target to the slot center (keep the hover height) and optionally scale or highlight the slot. Use a larger release radius than hover radius (hysteresis) so it does not flicker between slots.
- **Drop:** animate from the current position down to the slot, then lock. On invalid drop, animate back to the origin slot.
- **Clamp:** limit the target to the board bounds so the object cannot leave the playable area.
- **Rotation:** tilt slightly toward the movement direction using the velocity of the target; ease back to zero on drop.

## Edge cases

| Case | Handling |
|------|----------|
| Ray parallel to plane (camera near horizontal) | Return null and keep the last valid target |
| Plane behind camera (`t < 0`) | Same; never use the negative hit |
| Pointer leaves the canvas/window | Use pointer capture (web) or treat as cancel and return to origin |
| Multiple touches | Track the pointer id that started the drag, ignore others |
| High DPI / canvas CSS size differs from buffer | Normalize with the element's bounding rect, not `window.innerWidth` |
| Dragged object blocks the pick ray | Exclude it from picking, or pick against the plane and slots only |
| Overlapping slots | Choose the nearest, break ties by a stable order |
| Resolution or FOV change mid-drag | Recompute rays every frame; do not cache projected positions |

## Verify

- Unit test `intersectPlane` with known rays: straight down hits `(x, h, z)`; parallel returns null; plane behind returns null.
- Test `findSnapSlot`: inside radius snaps, outside returns null, occupied slots are skipped, nearest wins.
- Manual: drag at screen edges and at shallow camera angles; confirm no jump on pickup and no jitter on snap boundaries.
- Check frame-rate independence by capping to 30 and 144 fps and comparing the follow feel.
