import { auth } from "../utils/auth.js";

const BASE_URL = "http://127.0.0.1:5000/api";

export const apiClient = {
  async getPosts(status = null) {
    try {
      const url = status ? `${BASE_URL}/posts/?status=${status}` : `${BASE_URL}/posts/`;
      const response = await fetch(url);
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
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${auth.getToken()}`
        },
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
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${auth.getToken()}`
        },
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
        headers: {
          "Authorization": `Bearer ${auth.getToken()}`
        }
      });
      return response.ok;
    } catch (error) {
      console.error("Delete Error:", error);
      return false;
    }
  },
};
