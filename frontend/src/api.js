/**
 * api.js — API Client for TlaquaNet
 * ===================================
 * Centralized API calls to the FastAPI backend.
 * 
 * In development, requests go through the Vite proxy (see vite.config.js).
 * In production, set VITE_API_URL to your backend URL.
 */

// Base URL: Uses Vite proxy in dev, or environment variable in production
const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * Generic fetch wrapper with error handling
 */
async function request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: { 'Content-Type': 'application/json' },
        ...options,
    };

    const response = await fetch(url, config);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }

    // Handle 204 No Content (e.g., unlike)
    if (response.status === 204) return null;

    return response.json();
}

// ── Users ────────────────────────────────────────────────────

export const createUser = (username, displayName) =>
    request('/api/users/', {
        method: 'POST',
        body: JSON.stringify({ username, display_name: displayName }),
    });

export const getUsers = () =>
    request('/api/users/');

export const updateUser = (userId, displayName) =>
    request(`/api/users/${userId}`, {
        method: 'PUT',
        body: JSON.stringify({ display_name: displayName }),
    });

// ── Posts ─────────────────────────────────────────────────────

export const createPost = (content, authorId) =>
    request('/api/posts/', {
        method: 'POST',
        body: JSON.stringify({ content, author_id: authorId }),
    });

export const getPosts = (skip = 0, limit = 50) =>
    request(`/api/posts/?skip=${skip}&limit=${limit}`);

// ── Likes ────────────────────────────────────────────────────

export const likePost = (postId, userId) =>
    request(`/api/posts/${postId}/like`, {
        method: 'POST',
        body: JSON.stringify({ user_id: userId }),
    });

export const unlikePost = (postId, userId) =>
    request(`/api/posts/${postId}/like/${userId}`, {
        method: 'DELETE',
    });

// ── Comments ─────────────────────────────────────────────────

export const createComment = (postId, content, authorId) =>
    request(`/api/posts/${postId}/comments`, {
        method: 'POST',
        body: JSON.stringify({ content, author_id: authorId }),
    });

// ── Analytics ────────────────────────────────────────────────

export const getEvents = (eventType = null, limit = 100) => {
    let url = `/api/analytics/events?limit=${limit}`;
    if (eventType) url += `&event_type=${eventType}`;
    return request(url);
};

export const getSummary = () =>
    request('/api/analytics/summary');
