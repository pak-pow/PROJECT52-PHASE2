const BASE_URL = "http://127.0.0.1:5000/api";

export const auth = {
  async login(username, password) {
    try {
      const response = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Login failed");
      
      localStorage.setItem("cms_token", data.token);
      return true;
    } catch (error) {
      console.error("Login Error:", error);
      return false;
    }
  },

  logout() {
    localStorage.removeItem("cms_token");
  },

  getToken() {
    return localStorage.getItem("cms_token");
  },

  isAuthenticated() {
    return !!this.getToken();
  }
};
