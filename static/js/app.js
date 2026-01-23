console.log("Hello World!");

let state = {};
const state_endpoint = "/api/v1/state";

function fetch_current_State() {
  fetch(state_endpoint)
    .then((response) => response.json())
    .then((data) => {
      state = { ...data };
      update_state();
    })
    .catch((error) => {
      console.error("Error fetching bridge status:", error);
    });
}

function update_state() {
  document.getElementById("bridge-status").textContent = state.bridge_state;
  document.getElementById("timestamp").textContent = convert_timestamp(
    state.timestamp,
  );
}

function convert_timestamp(timestamp) {
  const date = new Date(timestamp);
  const estTime = date.toLocaleString("en-US", {
    timeZone: "America/New_York",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  });

  return estTime;
}

window.onload = function () {
  setInterval(fetch_current_State, 10000);
  fetch_current_State();
};
