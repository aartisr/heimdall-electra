import { createRootRoute, createRoute, createRouter, Outlet } from "@tanstack/react-router";
import { siteConfig } from "./site-config";
import { EvidenceConsole } from "./views/evidence-console";

const rootRoute = createRootRoute({
  component: () => (
    <main id="main-content">
      <a className="skip-link" href="#evidence-status">Skip to research status</a>
      <header className="site-header">
        <p className="eyebrow">{siteConfig.projectName}</p>
        <h1>{siteConfig.productName}</h1>
        <p className="header-summary">{siteConfig.shortDescription}</p>
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
