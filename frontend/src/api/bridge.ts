const API = {
  getBridgeState: "/api/v1/state",
};

export type BridgeStateResponse = {
  state_id: string;
  bridge_state: "CLOSED" | "CLOSING" | "OPEN" | "OPENING" | "UNKNOWN";
  timestamp: Date;
  last_event_id: string;
  can_update: boolean;
};

export const fetchBridgeState = async () => {
  try {
    const response = await fetch(API.getBridgeState);

    if (response.ok) {
      const { bridge_state, timestamp }: BridgeStateResponse =
        await response.json();
      return {
        bridgeState: bridge_state,
        timestamp,
      };
    }
  } catch (error) {
    console.error("Error fetching bridge status:", error);
  }
};
