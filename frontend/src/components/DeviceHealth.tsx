import { useEffect, useState } from "react";
import { fetchDeviceHealth } from "../api/events";

export function DeviceHealth() {
  const initialState = null;
  const [state, setState] = useState<any>(initialState);

  const updateState = async () => {
    const update = await fetchDeviceHealth();

    if (update) {
      setState({ ...update });
    }
  };

  useEffect(() => {
    updateState();
    const updateInterval = setInterval(updateState, 5000);

    return () => {
      clearInterval(updateInterval);
    };
  }, []);

  return (
    <>
      {state && (
        <div className="flex space-x-2">
          <div>
            <h4>CPU</h4>
            {state.cpu}
          </div>
          <div>
            <h4>RAM</h4>
            {state.ram}
          </div>
          <div>
            <h4>Temperature</h4>
            {state.temperature}
          </div>
          <div>
            <h4>Voltage</h4>
            {state.voltage}
          </div>
          <div>
            <h4>Active</h4>
            {state.is_online ? "Yes" : "No"}
          </div>
          <div>
            <h4>Last update</h4>
            {state.timestamp}
          </div>
        </div>
      )}
    </>
  );
}
