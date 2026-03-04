/**
 * App.jsx — Main Application Component
 * ======================================
 * The root component that manages:
 * - Tab navigation (Feed / Create User / Analytics)
 * - Current user selection (since there's no auth)
 * - Global state (users, posts, toast messages)
 */

import { useState, useEffect, useCallback } from 'react';
import { getUsers, getPosts, getSummary, updateUser } from './api.js';

import CreateUserForm from './components/CreateUserForm.jsx';
import CreatePostForm from './components/CreatePostForm.jsx';
import PostCard from './components/PostCard.jsx';
import AnalyticsPanel from './components/AnalyticsPanel.jsx';
import Toast from './components/Toast.jsx';

function App() {
    // ── State ──────────────────────────────────────────────────
    const [activeTab, setActiveTab] = useState('feed');
    const [users, setUsers] = useState([]);
    const [posts, setPosts] = useState([]);
    const [currentUser, setCurrentUser] = useState(null);
    const [summary, setSummary] = useState(null);
    const [toast, setToast] = useState(null);
    const [loading, setLoading] = useState(true);
    const [editingName, setEditingName] = useState('');
    const [isUpdating, setIsUpdating] = useState(false);

    // ── Data Fetching ──────────────────────────────────────────
    const fetchUsers = useCallback(async () => {
        try {
            const data = await getUsers();
            setUsers(data);
        } catch (err) {
            showToast(`Failed to load users: ${err.message}`, 'error');
        }
    }, []);

    const fetchPosts = useCallback(async () => {
        try {
            const data = await getPosts();
            setPosts(data);
        } catch (err) {
            showToast(`Failed to load posts: ${err.message}`, 'error');
        }
    }, []);

    const fetchSummary = useCallback(async () => {
        try {
            const data = await getSummary();
            setSummary(data);
        } catch (err) {
            console.error('Failed to fetch summary:', err);
        }
    }, []);

    const refreshAll = useCallback(async () => {
        setLoading(true);
        await Promise.all([fetchUsers(), fetchPosts(), fetchSummary()]);
        setLoading(false);
    }, [fetchUsers, fetchPosts, fetchSummary]);

    // Load data on mount
    useEffect(() => {
        refreshAll();
    }, [refreshAll]);

    // Update editingName when currentUser changes
    useEffect(() => {
        if (currentUser) {
            setEditingName(currentUser.display_name);
        } else {
            setEditingName('');
        }
    }, [currentUser]);

    // ── Toast Notifications ────────────────────────────────────
    const showToast = (message, type = 'success') => {
        setToast({ message, type, id: Date.now() });
        setTimeout(() => setToast(null), 3000);
    };

    // ── Event Handlers ─────────────────────────────────────────
    const handleUserCreated = (newUser) => {
        setUsers((prev) => [newUser, ...prev]);
        setCurrentUser(newUser);
        fetchSummary();
        showToast(`Welcome, ${newUser.display_name}! 🎉`);
        setActiveTab('feed');
    };

    const handlePostCreated = (newPost) => {
        setPosts((prev) => [newPost, ...prev]);
        fetchSummary();
        showToast('Post published! 📝');
    };

    const handlePostUpdated = () => {
        fetchPosts();
        fetchSummary();
    };

    const handleUpdateName = async () => {
        if (!currentUser || !editingName.trim() || editingName === currentUser.display_name) return;

        setIsUpdating(true);
        try {
            const updatedUser = await updateUser(currentUser.id, editingName.trim());

            // Update local users list
            setUsers(prev => prev.map(u => u.id === updatedUser.id ? updatedUser : u));

            // Update current user
            setCurrentUser(updatedUser);

            // Refresh posts to show new name
            fetchPosts();
            fetchSummary();

            showToast('Display name updated! ✨');
        } catch (err) {
            showToast(`Update failed: ${err.message}`, 'error');
        } finally {
            setIsUpdating(false);
        }
    };

    // ── Render ─────────────────────────────────────────────────
    return (
        <div className="app-container">
            {/* Header */}
            <header className="app-header">
                <h1>
                    <img src="/opossum.svg" alt="Opossum" className="logo" />
                    TlaquaNet
                </h1>
                <p>A didactic social network for data engineering students</p>
            </header>

            {/* User Selector */}
            {users.length > 0 && (
                <div className="user-selector">
                    <div className="section-title">
                        <span className="icon">👤</span>
                        Acting as:
                    </div>
                    <div className="user-chips">
                        {users.map((user) => (
                            <button
                                key={user.id}
                                className={`user-chip ${currentUser?.id === user.id ? 'active' : ''}`}
                                onClick={() => setCurrentUser(user)}
                                id={`user-chip-${user.id}`}
                            >
                                <span className="chip-avatar">
                                    {user.display_name.charAt(0).toUpperCase()}
                                </span>
                                {user.display_name}
                            </button>
                        ))}
                    </div>

                    {/* Quick Update Display Name */}
                    {currentUser && (
                        <div className="update-profile-bar">
                            <span style={{ fontSize: '1.2rem' }}>✏️</span>
                            <input
                                type="text"
                                value={editingName}
                                onChange={(e) => setEditingName(e.target.value)}
                                placeholder="Change display name..."
                                disabled={isUpdating}
                                onKeyDown={(e) => e.key === 'Enter' && handleUpdateName()}
                            />
                            {editingName !== currentUser.display_name && (
                                <button
                                    className="btn btn-primary update-btn"
                                    onClick={handleUpdateName}
                                    disabled={isUpdating || !editingName.trim()}
                                >
                                    {isUpdating ? '...' : 'Save'}
                                </button>
                            )}
                        </div>
                    )}
                </div>
            )}

            {/* Tab Navigation */}
            <nav className="tab-nav">
                {[
                    { id: 'feed', label: '📰 Feed' },
                    { id: 'create-user', label: '👤 New User' },
                    { id: 'analytics', label: '📊 Analytics' },
                ].map((tab) => (
                    <button
                        key={tab.id}
                        className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab.id)}
                        id={`tab-${tab.id}`}
                    >
                        {tab.label}
                    </button>
                ))}
            </nav>

            {/* Tab Content */}
            {activeTab === 'feed' && (
                <div>
                    {/* Create Post (only if user is selected) */}
                    {currentUser ? (
                        <CreatePostForm
                            currentUser={currentUser}
                            onPostCreated={handlePostCreated}
                            onError={(msg) => showToast(msg, 'error')}
                        />
                    ) : (
                        <div className="card" style={{ textAlign: 'center' }}>
                            <p style={{ color: 'var(--text-secondary)' }}>
                                👆 Select a user above or create a new one to start posting
                            </p>
                        </div>
                    )}

                    {/* Posts Feed */}
                    <div className="section-title" style={{ marginTop: 'var(--space-xl)' }}>
                        <span className="icon">📰</span>
                        Feed
                    </div>

                    {loading ? (
                        <div className="empty-state">
                            <div className="empty-icon">⏳</div>
                            <p>Loading posts...</p>
                        </div>
                    ) : posts.length === 0 ? (
                        <div className="empty-state">
                            <div className="empty-icon">📝</div>
                            <p>No posts yet. Be the first to post!</p>
                        </div>
                    ) : (
                        posts.map((post) => (
                            <PostCard
                                key={post.id}
                                post={post}
                                currentUser={currentUser}
                                onUpdated={handlePostUpdated}
                                onError={(msg) => showToast(msg, 'error')}
                                showToast={showToast}
                            />
                        ))
                    )}
                </div>
            )}

            {activeTab === 'create-user' && (
                <CreateUserForm
                    onUserCreated={handleUserCreated}
                    onError={(msg) => showToast(msg, 'error')}
                />
            )}

            {activeTab === 'analytics' && (
                <AnalyticsPanel summary={summary} />
            )}

            {/* Toast Notification */}
            {toast && <Toast message={toast.message} type={toast.type} key={toast.id} />}
        </div>
    );
}

export default App;
