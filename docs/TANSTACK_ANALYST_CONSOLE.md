# TanStack Research Evidence Console

## Purpose

The analyst console is a read-only transparency surface for research status, evidence classes, source limits, and stage-gate state. It is intentionally not an orbital-traffic display, candidate tracker, command console, or system of record.

## TanStack architecture

- TanStack Router provides typed route composition and is ready for future role-scoped routes.
- TanStack Query manages the read-only research-status resource and its freshness/retry policy.
- TanStack Table renders source metadata from declared columns rather than ad hoc table markup.
- Future TanStack Form workflows must be limited to governed review/approval proposals; the server repeats authorization and validation.
- Future live updates must invalidate narrowly scoped query keys and display stale/disconnected state.

## Current data boundary

The UI reads a static fixture in public/research-status.json. It is explicit about this limitation. A future read-only API must derive its response from the experiment ledger, source registry, model registry, and evidence catalog; it must not treat the browser snapshot as authoritative.

## Reuse, discoverability, and deployment

The console is deliberately reusable: project-facing labels live in `src/site-config.ts`; the governed snapshot stays in `public/research-status.json`; and the generated console has no project-specific command or secret path. For a new deployment, update both `site-config.ts` and the factual title/description/Open Graph metadata in `index.html`, regenerate the status snapshot from that project's authoritative registries, and run `npm run build`.

`public/robots.txt` allows indexing only because this repository's snapshot is public and non-sensitive. Change it to disallow indexing before deploying any restricted research material. A production host should also supply the final canonical URL and sitemap at the host/domain layer. They are intentionally not hard-coded here: a placeholder or a guessed domain would create misleading search metadata.

The page uses semantic headings, a real table caption, keyboard focus handling, a skip link, mobile table cards, and error recovery. These help people and crawlers understand the page, but neither technical SEO nor structured metadata can honestly guarantee ranking, virality, or inclusion in every search or AI-answering product.

## Security boundary

No secret, command path, privileged calculation, detector logic, or model decision runs in the browser. Before a server API is added, require route-level authorization, short-lived credentials, strict CSP, safe rendering, rate limiting, audit events, and server-side policy enforcement.
