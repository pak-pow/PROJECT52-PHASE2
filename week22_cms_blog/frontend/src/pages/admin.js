import { apiClient } from "../api/client.js";

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();
});

async function loadDashboard() {
  const tableBody = document.getElementById("posts-table-body");
  const posts = await apiClient.getPosts();
  tableBody.innerHTML = "";

  posts.forEach((post) => {
    const row = document.createElement("tr");

    row.innerHTML = `
            <td>${post.id}</td>
            <td><strong>${post.title}</strong></td>
            <td>${new Date(post.created_at).toLocaleDateString()}</td>
            <td>
                <button class="btn-edit">Edit</button>
                <button class="btn-delete">Delete</button>
            </td>
        `;

    const deleteBtn = row.querySelector(".btn-delete");

    deleteBtn.addEventListener("click", async () => {
      const confirmDelete = confirm(
        `Are you sure you want to delete "${post.title}"?`,
      );

      if (confirmDelete) {
        const success = await apiClient.deletePost(post.id);

        if (success) {
          loadDashboard();
        } else {
          alert("Failed to delete the post. Check the console.");
        }
      }
    });

    tableBody.appendChild(row);
  });
}
