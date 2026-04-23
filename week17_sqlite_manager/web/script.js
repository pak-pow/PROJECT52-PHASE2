// ==========================================
// GLOBAL CONFIGURATION & STATE
// ==========================================
const CONFIG = {
  API_BASE_URL: "http://127.0.0.1:5000/api/users",
  DOM_IDS: {
    TABLE_BODY: "userTableBody",
    FORM: "userForm",
    USERNAME_INPUT: "username",
    ROLE_INPUT: "role",
  },
  CLASSES: {
    DELETE_BTN: "delete-btn",
    EDIT_BTN: "edit-btn",
  },
};

const Utils = {
  escapeHTML(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  },
};

// ==========================================
// API SERVICE
// ==========================================
const ApiService = {
  async getUsers() {
    try {
      const response = await fetch(CONFIG.API_BASE_URL);
      if (!response.ok) throw new Error("Failed to fetch users.");
      return await response.json();
    } catch (error) {
      console.error(error);
      return [];
    }
  },

  async createUser(username, role) {
    try {
      const response = await fetch(CONFIG.API_BASE_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, role }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error);
      return data;
    } catch (error) {
      throw error;
    }
  },

  async updateUserRole(username, newRole) {
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/${username}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: newRole }),
      });
      if (!response.ok) throw new Error("Failed to update user.");
      return true;
    } catch (error) {
      console.error("API Error: ", error);
      throw error;
    }
  },

  async deleteUser(username) {
    try {
      const response = await fetch(`${CONFIG.API_BASE_URL}/${username}`, {
        method: "DELETE",
      });
      if (!response.ok) throw new Error("Failed to delete user.");
      return true;
    } catch (error) {
      throw error;
    }
  },
};

// ==========================================
// UI CONTROLLER (Interface Logic)
// ==========================================
const UIController = {
  elements: {},

  init() {
    this.elements = {
      tableBody: document.getElementById(CONFIG.DOM_IDS.TABLE_BODY),
      form: document.getElementById(CONFIG.DOM_IDS.FORM),
      username: document.getElementById(CONFIG.DOM_IDS.USERNAME_INPUT),
      role: document.getElementById(CONFIG.DOM_IDS.ROLE_INPUT),
    };

    this.setupEventListeners();
    this.loadAndRenderUsers();
  },

  setupEventListeners() {
    this.elements.form.addEventListener("submit", this.handleCreate.bind(this));
    this.elements.tableBody.addEventListener(
      "click",
      this.handleTableClick.bind(this),
    );
  },

  async loadAndRenderUsers() {
    const users = await ApiService.getUsers();
    this.elements.tableBody.innerHTML = "";

    const fragment = document.createDocumentFragment();

    users.forEach((user, index) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${index + 1}</td>
        <td>${Utils.escapeHTML(user.username)}</td>
        <td>${Utils.escapeHTML(user.role)}</td>
        <td>
          <button class="${CONFIG.CLASSES.EDIT_BTN}" data-username="${user.username}">Edit</button>
          <button class="${CONFIG.CLASSES.DELETE_BTN}" data-username="${user.username}">Delete</button>
        </td>
      `;
      fragment.appendChild(tr);
    });

    this.elements.tableBody.appendChild(fragment);
  },

  async handleCreate(event) {
    event.preventDefault();
    const username = this.elements.username.value.trim();
    const role = this.elements.role.value.trim();

    if (!username || !role) return;

    try {
      await ApiService.createUser(username, role);
      this.elements.form.reset();
      this.loadAndRenderUsers();
    } catch (error) {
      alert(error.message);
    }
  },

  async handleTableClick(event) {
    const target = event.target;

    if (target.classList.contains(CONFIG.CLASSES.DELETE_BTN)) {
      const username = target.dataset.username;

      if (confirm(`Are you sure you want to delete ${username}?`)) {
        try {
          await ApiService.deleteUser(username);
          this.loadAndRenderUsers();
        } catch (error) {
          alert("Could not delete user.");
        }
      }
    }

    if (target.classList.contains(CONFIG.CLASSES.EDIT_BTN)) {
      const username = target.dataset.username;

      const newRole = prompt(`Enter the new role for ${username}:`);

      if (newRole && newRole.trim() !== "") {
        try {
          await ApiService.updateUserRole(username, newRole.trim());
          this.loadAndRenderUsers();
        } catch (error) {
          alert("Could not update user role.");
        }
      }
    }
  },
};

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
  UIController.init();
});
