"use client";

import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// Shows whether the FastAPI backend is reachable. Handy during setup.
export default function ApiStatus() {
  const [status, setStatus] = useState<"checking" | "ok" | "down">("checking");

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((res) => (res.ok ? res.json() : Promise.reject()))
      .then((data) => setStatus(data.status === "ok" ? "ok" : "down"))
      .catch(() => setStatus("down"));
  }, []);

  const label = {
    checking: "Checking API…",
    ok: "API connected",
    down: `API not reachable at ${API_URL}`,
  }[status];

  const color = {
    checking: "bg-slate-400",
    ok: "bg-green-500",
    down: "bg-red-500",
  }[status];

  return (
    <p className="flex items-center gap-2 text-sm text-slate-600 dark:text-slate-400">
      <span className={`inline-block h-2 w-2 rounded-full ${color}`} />
      {label}
    </p>
  );
}
