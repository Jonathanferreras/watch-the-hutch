import { createFileRoute, useNavigate } from "@tanstack/react-router";

import { CameraFeed } from "../../components/CameraFeed";
import { DeviceHealth } from "../../components/DeviceHealth";
import { logoutUser, requireUser } from "../../api/auth";

export const Route = createFileRoute("/admin/dashboard")({
  component: AdminDashboardComponent,
  loader: () => requireUser(),
});

function AdminDashboardComponent() {
  const navigate = useNavigate();
  const currentUser = Route.useLoaderData();

  const handleLogout = async () => {
    await logoutUser();
    await navigate({ to: "/admin" });
  };

  return (
    <div className="p-4">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold">Admin Dashboard</h3>
          <p className="text-sm">
            Logged in as {currentUser.username} ({currentUser.role})
          </p>
        </div>
        <button className="rounded border px-3 py-2" onClick={handleLogout}>
          Logout
        </button>
      </div>
      <div>
        <h2>Camera Feed</h2>
        <CameraFeed maxWidth="768px" />
      </div>
      <div>
        <h2>Device Health</h2>
        <DeviceHealth />
      </div>
    </div>
  );
}
