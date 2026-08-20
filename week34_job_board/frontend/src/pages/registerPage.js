import { renderNavbar } from "../components/navbar.js";
import { registerUser } from "../api/authApi.js";
import { setStoredUser } from "../utils/authCheck.js";
import { showToast } from "../utils/helpers.js";

document.addEventListener("DOMContentLoaded", () => {
    renderNavbar("register");

    const registerForm = document.getElementById("register-form");
    const roleApplicantBtn = document.getElementById("role-applicant-btn");
    const roleEmployerBtn = document.getElementById("role-employer-btn");
    const roleInput = document.getElementById("register-role");
    const companyNameGroup = document.getElementById("company-name-group");

    // Toggle Applicant / Employer Roles
    roleApplicantBtn?.addEventListener("click", () => {
        roleApplicantBtn.classList.add("active");
        roleEmployerBtn.classList.remove("active");
        if (roleInput) roleInput.value = "applicant";
        if (companyNameGroup) companyNameGroup.style.display = "none";
    });

    roleEmployerBtn?.addEventListener("click", () => {
        roleEmployerBtn.classList.add("active");
        roleApplicantBtn.classList.remove("active");
        if (roleInput) roleInput.value = "employer";
        if (companyNameGroup) companyNameGroup.style.display = "flex";
    });

    registerForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById("register-submit-btn");
        if (submitBtn) submitBtn.disabled = true;

        const role = roleInput?.value || "applicant";
        const userData = {
            username: document.getElementById("register-username").value.trim(),
            email: document.getElementById("register-email").value.trim(),
            password: document.getElementById("register-password").value.trim(),
            role: role,
            company_name: role === "employer" ? document.getElementById("register-company")?.value.trim() : ""
        };

        try {
            showToast("Creating account...", "info");
            const data = await registerUser(userData);
            setStoredUser(data.user);
            showToast("Account created successfully! 🎉", "success");

            setTimeout(() => {
                if (data.user.role === "employer") {
                    window.location.href = "employer.html";
                } else {
                    window.location.href = "dashboard.html";
                }
            }, 500);
        } catch (err) {
            showToast(err.message || "Registration failed.", "error");
        } finally {
            if (submitBtn) submitBtn.disabled = false;
        }
    });
});
