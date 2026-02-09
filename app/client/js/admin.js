const API = {
  login: "/api/v1/admin/login",
  logout: "/api/v1/admin/logout",
  currentUser: "/api/v1/admin/me",
};

let currentAdmin = null;

const dom = {
  loginContainer: () => document.getElementById("login-container"),
  adminContainer: () => document.getElementById("admin-container"),
  adminUsername: () => document.getElementById("admin-username"),
  adminRoleBadge: () => document.getElementById("admin-role-badge"),
  loginForm: () => document.getElementById("login-form"),
  loginError: () => document.getElementById("login-error"),
  loginBtn: () => document.getElementById("login-btn"),
  logoutBtn: () => document.getElementById("logout-btn"),
  username: () => document.getElementById("username"),
  password: () => document.getElementById("password"),
  video: () => document.getElementById("v"),
};

async function checkAuth() {
  try {
    const response = await fetch(API.currentUser);
    if (response.ok) {
      const admin = await response.json();
      currentAdmin = admin;
      showAdminDashboard(admin);
    } else {
      showLoginForm();
    }
  } catch (error) {
    console.error("Error checking auth:", error);
    showLoginForm();
  }
}

function showLoginForm() {
  dom.loginContainer().style.display = "block";
  dom.adminContainer().classList.remove("active");
  currentAdmin = null;
}

function showAdminDashboard(admin) {
  dom.loginContainer().style.display = "none";
  dom.adminContainer().classList.add("active");
  dom.adminUsername().textContent = admin.username;

  const roleBadge = dom.adminRoleBadge();

  roleBadge.textContent = admin.role;
  roleBadge.className = `role-badge role-${admin.role.toLowerCase()}`;
}

async function handleLogin(event) {
  event.preventDefault();

  const username = dom.username().value;
  const password = dom.password().value;
  const loginBtn = dom.loginBtn();
  const errorDiv = dom.loginError();

  errorDiv.classList.remove("show");
  errorDiv.textContent = "";

  loginBtn.disabled = true;
  loginBtn.textContent = "Logging in...";

  try {
    const response = await fetch(API.login, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username: username,
        password: password,
      }),
    });

    if (response.ok) {
      const data = await response.json();
      currentAdmin = data.admin;
      showAdminDashboard(data.admin);
      dom.loginForm().reset();
    } else {
      const error = await response.json();
      errorDiv.textContent = error.detail || "Invalid username or password";
      errorDiv.classList.add("show");
    }
  } catch (error) {
    console.error("Login error:", error);
    errorDiv.textContent = "An error occurred during login. Please try again.";
    errorDiv.classList.add("show");
  } finally {
    loginBtn.disabled = false;
    loginBtn.textContent = "Login";
  }
}

async function handleLogout() {
  try {
    const response = await fetch(API.logout, {
      method: "POST",
    });

    if (response.ok) {
      showLoginForm();
      currentAdmin = null;
    } else {
      console.error("Logout error:", response);
      showLoginForm();
    }
  } catch (error) {
    console.error("Logout error:", error);
    showLoginForm();
  }
}

function initAuthUI() {
  dom.loginForm().addEventListener("submit", handleLogin);
  dom.logoutBtn().addEventListener("click", handleLogout);
  checkAuth();
}

function resolveWebRtcUrl(videoEl) {
  return videoEl.dataset.webrtcUrl || "/camera/whep";
}

function createPeerConnection() {
  return new RTCPeerConnection({ iceServers: [] });
}

function createInboundStream(videoEl, pc) {
  const inbound = new MediaStream();
  videoEl.srcObject = inbound;
  pc.addTransceiver("video", { direction: "recvonly" });

  pc.ontrack = async (ev) => {
    inbound.addTrack(ev.track);
    try {
      await videoEl.play();
    } catch (e) {
      console.warn("play blocked:", e);
    }
  };

  pc.oniceconnectionstatechange = () => {
    console.log("ICE connection state:", pc.iceConnectionState);
  };
  pc.onconnectionstatechange = () => {
    console.log("Peer connection state:", pc.connectionState);
  };

  return inbound;
}

async function waitForIceGatheringComplete(pc) {
  if (pc.iceGatheringState === "complete") return;
  await new Promise((resolve) => {
    const checkState = () => {
      if (pc.iceGatheringState === "complete") {
        pc.removeEventListener("icegatheringstatechange", checkState);
        resolve();
      }
    };
    pc.addEventListener("icegatheringstatechange", checkState);
  });
}

async function startWebRtc() {
  const videoEl = dom.video();
  if (!videoEl) return;

  const webrtcUrl = resolveWebRtcUrl(videoEl);
  const pc = createPeerConnection();

  createInboundStream(videoEl, pc);

  const offer = await pc.createOffer();
  await pc.setLocalDescription(offer);
  await waitForIceGatheringComplete(pc);

  const res = await fetch(webrtcUrl, {
    method: "POST",
    headers: { "Content-Type": "application/sdp" },
    body: pc.localDescription.sdp,
  });

  if (!res.ok) {
    throw new Error(`WebRTC signaling failed: ${res.status} ${res.statusText}`);
  }

  const answerSdp = await res.text();
  await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });
}

function init() {
  initAuthUI();
  startWebRtc().catch(console.error);
}

document.addEventListener("DOMContentLoaded", init);
