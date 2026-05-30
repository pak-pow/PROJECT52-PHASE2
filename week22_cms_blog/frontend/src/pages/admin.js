import { apiClient } from "../api/client.js";
import { auth } from "../utils/auth.js";

let currentEditId = null;

document.addEventListener("DOMContentLoaded", () => {
  if (!auth.isAuthenticated()) {
    document.getElementById("login-modal").style.display = "flex";
  } else {
    document.getElementById("dashboard-container").style.display = "block";
    loadDashboard();
  }
  setupModal();
  setupLogin();
});

function setupLogin() {
  const loginForm = document.getElementById("login-form");
  const logoutBtn = document.getElementById("logout-btn");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const user = document.getElementById("login-username").value;
      const pass = document.getElementById("login-password").value;
      const success = await auth.login(user, pass);
      if (success) {
        document.getElementById("login-modal").style.display = "none";
        document.getElementById("dashboard-container").style.display = "block";
        loadDashboard();
        showToast("Logged in successfully!", "success");
      } else {
        showToast("Login failed. Check credentials.", "error");
      }
    });
  }

  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      auth.logout();
      document.getElementById("dashboard-container").style.display = "none";
      document.getElementById("login-modal").style.display = "flex";
      showToast("Logged out successfully.", "success");
    });
  }
}

function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  if (!container) return;
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function setupModal() {
  const form = document.getElementById("post-form");
  const newPostBtn = document.getElementById("create-post-btn");
  const cancelBtn = document.getElementById("cancel-btn");

  newPostBtn.addEventListener("click", () => openModal());
  cancelBtn.addEventListener("click", () => closeModal());

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const payload = {
      title: document.getElementById("post-title").value,
      content: document.getElementById("post-content").value,
      status: document.getElementById("post-status").value,
    };

    let success = false;

    if (currentEditId) {
      success = await apiClient.updatePost(currentEditId, payload);
    } else {
      success = await apiClient.createPost(payload);
    }

    if (success) {
      closeModal();
      loadDashboard();
      showToast("Post saved successfully!", "success");
    } else {
      showToast("Error saving post. Check console.", "error");
    }
  });
}

function openModal(post = null) {
  const modal = document.getElementById("post-modal");
  const titleInput = document.getElementById("post-title");
  const contentInput = document.getElementById("post-content");
  const modalTitle = document.getElementById("modal-title");
  const statusInput = document.getElementById("post-status");

  if (post) {
    currentEditId = post.id;
    modalTitle.textContent = "Edit Post";
    titleInput.value = post.title;
    contentInput.value = post.content;
    statusInput.value = post.status;
  } else {
    currentEditId = null;
    modalTitle.textContent = "Create New Post";
    titleInput.value = "";
    contentInput.value = "";
    statusInput.value = "draft";
  }

  modal.style.display = "flex";
}

function closeModal() {
  document.getElementById("post-modal").style.display = "none";
}

async function loadDashboard() {
  const tableBody = document.getElementById("posts-table-body");
  const posts = await apiClient.getPosts();
  tableBody.innerHTML = "";

  posts.forEach((post) => {
    const row = document.createElement("tr");

    row.innerHTML = `
            <td>${post.id}</td>
            <td><strong>${post.title}</strong> <span style="font-size:0.8em; padding:2px 6px; background:#444; border-radius:4px; margin-left:10px;">${post.status.toUpperCase()}</span></td>
            <td>${new Date(post.created_at).toLocaleDateString()}</td>
            <td>
                <button class="btn-edit">Edit</button>
                <button class="btn-delete">Delete</button>
            </td>
        `;

    const deleteBtn = row.querySelector(".btn-delete");
    deleteBtn.addEventListener("click", async () => {
      if (confirm(`Delete "${post.title}"?`)) {
        if (await apiClient.deletePost(post.id)) loadDashboard();
      }
    });

    const editBtn = row.querySelector(".btn-edit");
    editBtn.addEventListener("click", () => {
      openModal(post);
    });

    tableBody.appendChild(row);
  });
}
