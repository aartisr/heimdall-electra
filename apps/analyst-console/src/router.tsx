import { createRootRoute, createRoute, createRouter, Outlet } from "@tanstack/react-router";
import { EvidenceConsole } from "./views/evidence-console";

const rootRoute = createRootRoute({
  component: () => (
    <main>
      <header className="site-header">
        <p className="eyebrow">Project Heimdall</p>
        <h1>Research Evidence Console</h1>
      </header>
      <Outlet />
    </main>
  ),
});

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/",
  component: EvidenceConsole,
});

const routeTree = rootRoute.addChildren([indexRoute]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}

