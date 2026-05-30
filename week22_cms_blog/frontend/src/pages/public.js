import { apiClient } from "../api/client.js";

document.addEventListener("DOMContentLoaded", () => {
  loadBlogFeed();
});

async function loadBlogFeed() {
  const feedContainer = document.getElementById("blog-feed");

  const posts = await apiClient.getPosts('published');

  feedContainer.innerHTML = "";

  if (posts.length === 0) {
    feedContainer.innerHTML =
      "<p>No posts available yet. Check back later!</p>";
    return;
  }

  posts.forEach((post) => {
    const article = document.createElement("article");
    article.className = "post-card";

    const parsedContent = DOMPurify.sanitize(marked.parse(post.content));

    article.innerHTML = `
            <h2 class="post-title">${post.title}</h2>
            <span class="post-date">Published on ${new Date(post.created_at).toLocaleDateString()}</span>
            <div class="post-content">${parsedContent}</div>
        `;

    feedContainer.appendChild(article);
  });
}
