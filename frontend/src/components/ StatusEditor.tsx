import { useEffect, useState } from "react";

import {
  fetchBridgeState,
  toggleBridgeUpdates,
  type BridgeState,
  type BridgeStatus,
  updateBridgeState,
} from "../api/bridge";
import { formatTimestamp } from "../utils/time";

const STATUS_OPTIONS: BridgeStatus[] = [
  "OPEN",
  "OPENING",
  "CLOSED",
  "CLOSING",
  "UNKNOWN",
];

export function StatusEditor() {
  const [currentState, setCurrentState] = useState<BridgeState | null>(null);
  const [updateError, setUpdateError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isToggling, setIsToggling] = useState(false);
  const [stateSelection, setStateSelection] = useState<BridgeStatus>("UNKNOWN");

  const loadCurrentState = async () => {
    const state = await fetchBridgeState();

    if (state) {
      setCurrentState(state);
      setStateSelection(state.bridgeState);
    }
  };

  useEffect(() => {
    loadCurrentState();
  }, []);

  const handleToggle = async () => {
    if (!currentState) {
      return;
    }

    setUpdateError("");
    setIsToggling(true);

    try {
      const updatedState = await toggleBridgeUpdates(!currentState.canUpdate);

      if (!updatedState) {
        throw new Error("Unable to update bridge mode.");
      }

      setCurrentState(updatedState);
    } catch (error) {
      setUpdateError(
        error instanceof Error ? error.message : "Unable to update bridge mode.",
      );
    } finally {
      setIsToggling(false);
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setUpdateError("");
    setIsSubmitting(true);

    try {
      const updatedState = await updateBridgeState(stateSelection);

      if (!updatedState) {
        throw new Error("Unable to update bridge state.");
      }

      setCurrentState(updatedState);
      setStateSelection(updatedState.bridgeState);
    } catch (error) {
      setUpdateError(
        error instanceof Error ? error.message : "Unable to update bridge state.",
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const isAuto = currentState?.canUpdate ?? false;

  return (
    <section className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.24em] text-slate-400">
            Status editor
          </p>
          <p className="text-sm font-semibold text-slate-800">
            {currentState ? currentState.bridgeState : "Loading..."}
          </p>
        </div>
        <div className="rounded-full border border-slate-200 bg-white px-3 py-1.5">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-600">
            <span className={!isAuto ? "text-slate-900" : "text-slate-400"}>
              Manual
            </span>

            <button
              type="button"
              onClick={handleToggle}
              disabled={!currentState || isToggling}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors disabled:cursor-not-allowed disabled:opacity-60 ${
                isAuto ? "bg-emerald-500" : "bg-slate-300"
              }`}
              aria-label={`Switch to ${isAuto ? "manual" : "auto"} mode`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isAuto ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>

            <span className={isAuto ? "text-slate-900" : "text-slate-400"}>
              Auto
            </span>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="grid gap-3 md:grid-cols-[minmax(0,1fr)_auto]">
          <div className="rounded-xl border border-slate-200 bg-white px-3 py-3">
            <p className="text-[11px] uppercase tracking-[0.22em] text-slate-400">
              Bridge state
            </p>
            <select
              value={stateSelection}
              onChange={(event) =>
                setStateSelection(event.target.value as BridgeStatus)
              }
              className="mt-2 w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium text-slate-800 outline-none transition focus:border-slate-400"
            >
              {STATUS_OPTIONS.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={isSubmitting}
            className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-800 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isSubmitting ? "Updating..." : "Update state"}
          </button>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600">
          <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
            <span>
              Mode:{" "}
              <span className="font-semibold text-slate-800">
                {isAuto ? "Auto updates enabled" : "Manual lock active"}
              </span>
            </span>
            <span>
              Last change:{" "}
              <span className="font-semibold text-slate-800">
                {currentState ? formatTimestamp(currentState.timestamp) : "--"}
              </span>
            </span>
          </div>
        </div>
      </form>

      {updateError ? (
        <p className="mt-2 text-sm text-red-600">{updateError}</p>
      ) : null}
    </section>
  );
}
