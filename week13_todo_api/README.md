# 📝 Week 13: Todo REST API (Backend)

Welcome to Week 13 of **PROJECT52**! This project is a fully functional backend REST API built with Python and Flask. It serves as the data engine for a Todo application, handling data validation, Cross-Origin Resource Sharing (CORS), and permanent flat-file storage.

## 🚀 Features

- **Complete CRUD Operations:** Create, Read, Update, and Delete tasks.
- **Persistent Data Storage:** Uses Python's `json` and `os` modules to permanently store state in a physical `todos.json` file. Data survives server reboots.
- **Input Validation:** Backend logic explicitly rejects empty strings or malformed payloads, returning standard `400 Bad Request` HTTP status codes.
- **CORS Enabled:** Fully prepared for frontend integration (Week 14) via the `flask-cors` library.

## 🛠️ Tech Stack

- **Language:** Python 3
- **Framework:** Flask
- **Middleware:** Flask-CORS
- **Storage:** Local JSON Flat-File
- **Testing:** Thunder Client (VS Code Extension)

---

## 📡 API Endpoints Reference

Base URL: `http://127.0.0.1:5000`

| Method     | Endpoint      | Description                 | Request Body (JSON)                        |
| :--------- | :------------ | :-------------------------- | :----------------------------------------- |
| **GET**    | `/`           | Server Health Check         | `None`                                     |
| **GET**    | `/todos`      | Retrieve all tasks          | `None`                                     |
| **POST**   | `/todos`      | Create a new task           | `{"task": "String"}`                       |
| **PUT**    | `/todos/<id>` | Update task / Mark Complete | `{"task": "String", "completed": Boolean}` |
| **DELETE** | `/todos/<id>` | Delete a specific task      | `None`                                     |

---

## 💻 How to Run Locally

**1. Clone the repository and navigate to the directory:**

```bash
cd VSCODE_PROJECT52/week13_todo_api
```

**2. Install required dependencies:**
Ensure you have Flask and Flask-CORS installed.

```bash
pip install flask flask-cors
```

**3. Boot the Server:**

```bash
python app.py
```

_The server will initialize on port 5000. If `todos.json` does not exist, the script will automatically generate it in the absolute path directory upon the first POST request._
