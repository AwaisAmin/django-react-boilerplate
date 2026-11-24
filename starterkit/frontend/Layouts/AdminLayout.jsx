import { AppShell } from "@/Layouts/AppShell"

const ROOT = { label: "Admin", route: "admin_dashboard", subtitle: "Admin console" }

/**
 * Shell for admin pages. Pages opt in with
 * `Page.layout = (page) => <AdminLayout breadcrumbs={[...]}>{page}</AdminLayout>`;
 * the component type never changes, so Inertia keeps it mounted across visits.
 */
export function AdminLayout({ breadcrumbs, children }) {
  return (
    <AppShell root={ROOT} breadcrumbs={breadcrumbs}>
      {children}
    </AppShell>
  )
}
