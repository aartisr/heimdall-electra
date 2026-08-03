import { createRootRoute, createRoute, createRouter, Outlet, Link } from "@tanstack/react-router";
import { siteConfig } from "./site-config";
import { EvidenceConsole } from "./views/evidence-console";
import { VisualizationPage } from "./views/visualization-page";

const rootRoute = createRootRoute({
  component: () => (
    <main id="main-content">
      <a className="skip-link" href="#main-nav">Skip to navigation</a>
      <header className="site-header">
        <p className="eyebrow">{siteConfig.projectName}</p>
        <h1>{siteConfig.productName}</h1>
        <p className="header-summary">{siteConfig.shortDescription}</p>
        <nav className="site-nav" id="main-nav" aria-label="Main navigation">
          <Link to="/"              className="nav-link" activeProps={{ className: "nav-link active" }}>Evidence Console</Link>
          <Link to="/visualization" className="nav-link" activeProps={{ className: "nav-link active" }}>Debris Visualization</Link>
        </nav>
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

const vizRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: "/visualization",
  component: VisualizationPage,
});

const routeTree = rootRoute.addChildren([indexRoute, vizRoute]);

export const router = createRouter({ routeTree });

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
