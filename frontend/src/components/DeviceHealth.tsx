import { useEffect, useState } from "react";
import { fetchDeviceHealth } from "../api/events";
import { formatTimestamp } from "../utils/time";

type DeviceHealthState = {
  cpu: string;
  ram: string;
  temperature: string;
  voltage: string;
  isOnline: boolean;
  timestamp: string;
};

function parseNumericValue(value: string) {
  const match = value.match(/-?\d+(\.\d+)?/);
  return match ? Number(match[0]) : null;
}

function formatPercent(value: string) {
  const parsed = parseNumericValue(value);
  if (parsed === null) {
    return { label: "--", value: 0 };
  }

  return {
    label: `${Math.round(parsed)}%`,
    value: Math.max(0, Math.min(100, parsed)),
  };
}

function formatTemperature(value: string) {
  const parsed = parseNumericValue(value);

  if (parsed === null) {
    return {
      label: "--",
      meta: "No reading",
      colorClass: "text-slate-500",
      dotClass: "bg-slate-300",
    };
  }

  if (parsed < 60) {
    return {
      label: `${Math.round(parsed)}C`,
      meta: "Optimal",
      colorClass: "text-emerald-600",
      dotClass: "bg-emerald-500",
    };
  }

  if (parsed < 75) {
    return {
      label: `${Math.round(parsed)}C`,
      meta: "Warning",
      colorClass: "text-amber-600",
      dotClass: "bg-amber-500",
    };
  }

  return {
    label: `${Math.round(parsed)}C`,
    meta: "Critical",
    colorClass: "text-rose-600",
    dotClass: "bg-rose-500",
  };
}

function formatVoltage(value: string) {
  const parsed = parseNumericValue(value);

  if (parsed === null) {
    return { label: "--", meta: "Unknown" };
  }

  if (parsed >= 12) {
    return { label: `${parsed.toFixed(1)}V`, meta: "Stable" };
  }

  if (parsed >= 11) {
    return { label: `${parsed.toFixed(1)}V`, meta: "Low" };
  }

  return { label: `${parsed.toFixed(1)}V`, meta: "Critical" };
}

function Gauge({
  label,
  value,
  accent,
}: {
  label: string;
  value: { label: string; value: number };
  accent: string;
}) {
  const background = `conic-gradient(${accent} ${value.value * 3.6}deg, #e5e7eb 0deg)`;

  return (
    <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2">
      <div
        className="grid h-12 w-12 shrink-0 place-items-center rounded-full"
        style={{ background }}
      >
        <div className="grid h-9 w-9 place-items-center rounded-full bg-white text-[11px] font-semibold text-slate-700">
          {Math.round(value.value)}
        </div>
      </div>
      <div>
        <p className="text-[11px] uppercase tracking-[0.22em] text-slate-400">
          {label}
        </p>
        <p className="text-sm font-semibold text-slate-800">{value.label}</p>
      </div>
    </div>
  );
}

function Stat({
  label,
  value,
  meta,
  valueClass = "text-slate-800",
  leading,
}: {
  label: string;
  value: string;
  meta: string;
  valueClass?: string;
  leading?: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white px-3 py-2">
      <div className="flex items-center gap-2">
        {leading}
        <p className="text-[11px] uppercase tracking-[0.22em] text-slate-400">
          {label}
        </p>
      </div>
      <p className={`mt-1 text-sm font-semibold ${valueClass}`}>{value}</p>
      <p className="text-xs text-slate-500">{meta}</p>
    </div>
  );
}

export function DeviceHealth() {
  const [state, setState] = useState<DeviceHealthState | null>(null);

  const updateState = async () => {
    const update = await fetchDeviceHealth();

    if (update) {
      setState(update);
    }
  };

  useEffect(() => {
    updateState();
    const updateInterval = setInterval(updateState, 5000);

    return () => {
      clearInterval(updateInterval);
    };
  }, []);

  if (!state) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">
        Waiting for telemetry...
      </div>
    );
  }

  const cpu = formatPercent(state.cpu);
  const ram = formatPercent(state.ram);
  const temperature = formatTemperature(state.temperature);
  const voltage = formatVoltage(state.voltage);

  return (
    <section className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
      <div className="flex flex-wrap items-center gap-3">
        <div className="mr-1 min-w-[150px]">
          <p className="text-[11px] uppercase tracking-[0.24em] text-slate-400">
            Device health
          </p>
          <div className="mt-1 flex items-center gap-2">
            <span
              className={`h-2.5 w-2.5 rounded-full ${
                state.isOnline
                  ? "bg-emerald-500 shadow-[0_0_10px_rgba(34,197,94,0.7)]"
                  : "bg-rose-500 shadow-[0_0_10px_rgba(244,63,94,0.6)]"
              }`}
            />
            <span className="text-sm font-semibold text-slate-800">
              {state.isOnline ? "Online" : "Offline"}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Updated {formatTimestamp(state.timestamp + "Z")}
          </p>
        </div>

        <Gauge label="CPU" value={cpu} accent="#3b82f6" />
        <Gauge label="RAM" value={ram} accent="#10b981" />

        <Stat
          label="Temperature"
          value={temperature.label}
          meta={temperature.meta}
          valueClass={temperature.colorClass}
          leading={
            <span className={`h-2 w-2 rounded-full ${temperature.dotClass}`} />
          }
        />

        <Stat
          label="Voltage"
          value={voltage.label}
          meta={voltage.meta}
          valueClass="text-sky-700"
        />
      </div>
    </section>
  );
}
