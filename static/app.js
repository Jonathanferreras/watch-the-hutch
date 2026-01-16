console.log("Hello World!");

const state = {};

function fetch_bridge_status() {
  // TODO: Update this once state endpoint is complete
  // fetch("/api/v1/state")
  //   .then((response) => response.json())
  //   .then((data) => {
  //     state = { ...data }
  //     update_bridge_status();
  //   })
  //   .catch((error) => {
  //     console.error("Error fetching bridge status:", error);
  //   });
}

function update_bridge_status() {
  // TODO: Update this once state endpoint is complete
  // document.getElementById("bridge-status").textContent = state.bridge_status;
  // document.getElementById("timestamp").textContent = state.timestamp;
}

window.onload = function () {
  setInterval(fetch_bridge_status, 10000);
  fetch_bridge_status();
};
