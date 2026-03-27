import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { fetchBridgeState } from "../api/bridge";

export const Route = createFileRoute("/")({
  component: HomeComponent,
  loader: () => fetchBridgeState(),
});

function HomeComponent() {
  const initialState = Route.useLoaderData();
  const [state, setState] = useState<any>(initialState);

  useEffect(() => {
    const updateInterval = setInterval(updateState, 5000);

    return () => {
      clearInterval(updateInterval);
    };
  }, []);

  const updateState = async () => {
    const bridgeState = await fetchBridgeState();

    if (bridgeState) {
      setState({ ...bridgeState });
    }
  };

  const renderState = () => {
    if (state?.bridgeState) {
      return (
        <ul>
          <li>{state.bridgeState}</li>
          <li>{state.timestamp}</li>
        </ul>
      );
    } else {
      return <></>;
    }
  };

  return (
    <div className="p-2">
      <h3>Watch the Hutch</h3>
      {renderState()}
    </div>
  );
}
