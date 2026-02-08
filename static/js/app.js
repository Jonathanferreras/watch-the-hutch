console.log("Hello World!");

const API = {
  state: "/api/v1/state",
};

const dom = {
  bridgeStatus: () => document.getElementById("bridge-status"),
  timestamp: () => document.getElementById("timestamp"),
};

let state = {};

async function fetchCurrentState() {
  try {
    const response = await fetch(API.state);
    const data = await response.json();
    state = { ...data };
    updateState();
  } catch (error) {
    console.error("Error fetching bridge status:", error);
  }
}

function updateState() {
  dom.bridgeStatus().textContent = state.bridge_state;
  dom.timestamp().textContent = formatTimestamp(state.timestamp);
}

function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleString("en-US", {
    timeZone: "America/New_York",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });
}

function init() {
  setInterval(fetchCurrentState, 10000);
  fetchCurrentState();
}

window.addEventListener("load", init);
