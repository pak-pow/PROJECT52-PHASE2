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

    tableBody.appendChild(row);
  });
}
