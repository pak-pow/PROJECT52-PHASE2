const BASE_URL = "http://127.0.0.1:5000/api";

export const apiClient = {
  async getPosts() {
    try {
      const response = await fetch(`${BASE_URL}/posts/`);
      if (!response.ok) throw new Error(`Failed to fetch posts`);
      return await response.json();
    } catch (error) {
      console.error("API Error:", error);
      return [];
    }
  },

  async createPost(data) {
    try {
      const response = await fetch(`${BASE_URL}/posts/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.ok;
    } catch (error) {
      console.error("Create Error:", error);
      return false;
    }
  },

  async updatePost(id, data) {
    try {
      const response = await fetch(`${BASE_URL}/posts/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      return response.ok;
    } catch (error) {
      console.error("Update Error:", error);
      return false;
    }
  },

  async deletePost(id) {
    try {
      const response = await fetch(`${BASE_URL}/posts/${id}`, {
        method: "DELETE",
      });
      return response.ok;
    } catch (error) {
      console.error("Delete Error:", error);
      return false;
    }
  },
};
