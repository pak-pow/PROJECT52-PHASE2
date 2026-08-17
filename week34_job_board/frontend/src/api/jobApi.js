const API_BASE_URL = "http://127.0.0.1:5000/api";

export async function fetchJobs(filters = {}) {
    const params = new URLSearchParams();
    if (filters.keyword) params.append("keyword", filters.keyword);
    if (filters.location) params.append("location", filters.location);
    if (filters.type) params.append("type", filters.type);
    if (filters.category) params.append("category", filters.category);
    if (filters.min_salary) params.append("min_salary", filters.min_salary);

    const res = await fetch(`${API_BASE_URL}/jobs?${params.toString()}`);
    if (!res.ok) throw new Error("Failed to fetch job listings.");
    return await res.json();
}

export async function fetchJobById(jobId) {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
    if (!res.ok) throw new Error("Job listing not found.");
    return await res.json();
}

export async function createJobPosting(jobData) {
    const res = await fetch(`${API_BASE_URL}/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(jobData)
    });
    if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || "Failed to create job posting.");
    }
    return await res.json();
}

export async function deleteJobPosting(jobId) {
    const res = await fetch(`${API_BASE_URL}/jobs/${jobId}`, {
        method: "DELETE"
    });
    if (!res.ok) throw new Error("Failed to delete job posting.");
    return await res.json();
}
