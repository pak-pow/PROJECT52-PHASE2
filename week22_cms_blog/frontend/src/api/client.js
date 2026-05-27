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
};
