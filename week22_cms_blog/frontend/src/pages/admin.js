import { apiClient } from "../api/client.js";

let currentEditId = null;

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
  setupModal();
});

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
      author_id: 1,
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
    } else {
      alert("Error saving post. Check console.");
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
