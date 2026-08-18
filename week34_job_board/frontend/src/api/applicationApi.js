const API_BASE_URL = "http://127.0.0.1:5000/api";

export async function submitApplication(formData) {
    // Accepts FormData containing job_id, applicant_name, applicant_email, cover_letter, and resume File
    const res = await fetch(`${API_BASE_URL}/applications`, {
        method: "POST",
        body: formData
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Failed to submit job application.");
    }
    return await res.json();
}

export async function toggleSavedJob(userId, jobId) {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/saved-jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: jobId })
    });
    if (!res.ok) throw new Error("Failed to update saved job status.");
    return await res.json();
}

export async function fetchSavedJobs(userId) {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/saved-jobs`);
    if (!res.ok) throw new Error("Failed to fetch saved jobs.");
    return await res.json();
}

export async function fetchApplicantApplications(userId) {
    const res = await fetch(`${API_BASE_URL}/users/${userId}/applications`);
    if (!res.ok) throw new Error("Failed to fetch user applications.");
    return await res.json();
}

export async function updateApplicationStatus(appId, status) {
    const res = await fetch(`${API_BASE_URL}/applications/${appId}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });
    if (!res.ok) throw new Error("Failed to update application status.");
    return await res.json();
}
