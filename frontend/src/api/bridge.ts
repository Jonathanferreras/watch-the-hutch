const API = {
  getBridgeState: "/api/v1/state",
  updateBridgeState: "/api/v1/state",
  toggleBridgeUpdates: "/api/v1/state/can_update",
};

export type BridgeStatus =
  | "CLOSED"
  | "CLOSING"
  | "OPEN"
  | "OPENING"
  | "UNKNOWN";

type BridgeStateResponse = {
  state_id: string;
  bridge_state: BridgeStatus;
  timestamp: string;
  last_event_id: string;
  can_update: boolean;
};

export type BridgeState = {
  stateId: string;
  bridgeState: BridgeStatus;
  timestamp: string;
  lastEventId: string;
  canUpdate: boolean;
};

function mapBridgeState(response: BridgeStateResponse): BridgeState {
  return {
    stateId: response.state_id,
    bridgeState: response.bridge_state,
    timestamp: response.timestamp,
    lastEventId: response.last_event_id,
    canUpdate: response.can_update,
  };
}

export const fetchBridgeState = async () => {
  try {
    const response = await fetch(API.getBridgeState);

    if (response.ok) {
      return mapBridgeState((await response.json()) as BridgeStateResponse);
    }
  } catch (error) {
    console.error("Error fetching bridge status:", error);
  }
};

export const updateBridgeState = async (bridgeState: BridgeStatus) => {
  try {
    const requestOptions: RequestInit = {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        bridge_state: bridgeState,
      }),
    };
    const response = await fetch(API.updateBridgeState, requestOptions);

    if (response.ok) {
      return mapBridgeState((await response.json()) as BridgeStateResponse);
    }
  } catch (error) {
    console.error("Error updating bridge status:", error);
  }
};

export const toggleBridgeUpdates = async (value: boolean) => {
  try {
    const response = await fetch(`${API.toggleBridgeUpdates}?value=${value}`, {
      method: "POST",
      credentials: "include",
    });

    if (response.ok) {
      return mapBridgeState((await response.json()) as BridgeStateResponse);
    }
  } catch (error) {
    console.error("Error toggling bridge updates:", error);
  }
};
