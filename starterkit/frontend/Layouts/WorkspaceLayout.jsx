import { AppShell } from "@/Layouts/AppShell"

const ROOT = { label: "Workspace", route: "workspace", subtitle: "Budget requests" }

/** Shell for pages open to every role. Used like AdminLayout. */
export function WorkspaceLayout({ breadcrumbs, children }) {
  return (
    <AppShell root={ROOT} breadcrumbs={breadcrumbs}>
      {children}
    </AppShell>
  )
}
