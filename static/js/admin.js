// Admin page JavaScript

let currentAdmin = null;
const login_endpoint = "/api/v1/admin/login";
const logout_endpoint = "/api/v1/admin/logout";
const current_user_endpoint = "/api/v1/admin/me";

// Check authentication status on page load
async function checkAuth() {
  try {
    const response = await fetch(current_user_endpoint);
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

// Show login form
function showLoginForm() {
  document.getElementById("login-container").style.display = "block";
  document.getElementById("admin-container").classList.remove("active");
  currentAdmin = null;
}

// Show admin dashboard
function showAdminDashboard(admin) {
  document.getElementById("login-container").style.display = "none";
  document.getElementById("admin-container").classList.add("active");

  // Update admin info
  document.getElementById("admin-username").textContent = admin.username;

  // Update role badge
  const roleBadge = document.getElementById("admin-role-badge");
  roleBadge.textContent = admin.role;
  roleBadge.className = `role-badge role-${admin.role.toLowerCase()}`;

  // Show/hide sections based on role
  const viewerSection = document.getElementById("viewer-section");
  const editorSection = document.getElementById("editor-section");
  const adminSection = document.getElementById("admin-section");

  // Viewer can always see viewer section
  viewerSection.style.display = "block";

  // Editor and Admin can see editor section
  if (admin.role === "EDITOR" || admin.role === "ADMIN") {
    editorSection.style.display = "block";
  } else {
    editorSection.style.display = "none";
  }

  // Only Admin can see admin section
  if (admin.role === "ADMIN") {
    adminSection.style.display = "block";
  } else {
    adminSection.style.display = "none";
  }
}

// Handle login form submission
async function handleLogin(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;
  const loginBtn = document.getElementById("login-btn");
  const errorDiv = document.getElementById("login-error");

  // Clear previous errors
  errorDiv.classList.remove("show");
  errorDiv.textContent = "";

  // Disable button during request
  loginBtn.disabled = true;
  loginBtn.textContent = "Logging in...";

  try {
    const response = await fetch(login_endpoint, {
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
      // Clear form
      document.getElementById("login-form").reset();
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
    const response = await fetch(logout_endpoint, {
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

window.onload = function () {
  document.getElementById("login-form").addEventListener("submit", handleLogin);
  document.getElementById("logout-btn").addEventListener("click", handleLogout);

  checkAuth();
};
