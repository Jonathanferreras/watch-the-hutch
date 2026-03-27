import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useState, type SyntheticEvent } from "react";

import { loginUser, verifyUser } from "../../api/auth";

export const Route = createFileRoute("/admin/")({
  component: AdminLoginComponent,
  loader: async () => {
    const currentUser = await verifyUser();

    if (currentUser) {
      throw redirect({
        to: "/admin/dashboard",
      });
    }

    return null;
  },
});

function AdminLoginComponent() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event: SyntheticEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await loginUser({ username, password });
      await navigate({ to: "/admin/dashboard" });
    } catch (submitError) {
      if (submitError instanceof Error) {
        setError(submitError.message);
      } else {
        setError("Unable to login");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4">
      <h3 className="mb-4 text-lg font-semibold">Admin Login</h3>
      <form className="flex max-w-sm flex-col gap-3" onSubmit={handleSubmit}>
        <input
          className="rounded border px-3 py-2"
          name="username"
          placeholder="Username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />
        <input
          className="rounded border px-3 py-2"
          name="password"
          placeholder="Password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
        <button
          className="rounded border px-3 py-2"
          disabled={isLoading}
          type="submit"
        >
          {isLoading ? "Logging in..." : "Login"}
        </button>
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
      </form>
    </div>
  );
}
