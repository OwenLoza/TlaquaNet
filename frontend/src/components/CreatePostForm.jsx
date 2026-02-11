/**
 * CreatePostForm.jsx — New Post Component
 * =========================================
 * Allows the selected user to create a new text post.
 */

import { useState } from 'react';
import { createPost } from '../api.js';

function CreatePostForm({ currentUser, onPostCreated, onError }) {
    const [content, setContent] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!content.trim()) return;

        setSubmitting(true);
        try {
            const newPost = await createPost(content.trim(), currentUser.id);
            onPostCreated(newPost);
            setContent('');
        } catch (err) {
            onError(err.message);
        } finally {
            setSubmitting(false);
        }
    };

    const charCount = content.length;
    const maxChars = 500;

    return (
        <form className="card" onSubmit={handleSubmit}>
            <div className="post-header" style={{ marginBottom: 'var(--space-sm)' }}>
                <div className="post-avatar">
                    {currentUser.display_name.charAt(0).toUpperCase()}
                </div>
                <div className="post-author-info">
                    <div className="post-display-name">{currentUser.display_name}</div>
                    <div className="post-username">@{currentUser.username}</div>
                </div>
            </div>

            <div className="form-group">
                <textarea
                    id="post-content"
                    className="form-textarea"
                    placeholder="What's on your mind? Share something with the class..."
                    value={content}
                    onChange={(e) => setContent(e.target.value)}
                    maxLength={maxChars}
                    rows={3}
                />
                <div
                    style={{
                        textAlign: 'right',
                        fontSize: 'var(--font-size-xs)',
                        color: charCount > 450 ? 'var(--like-color)' : 'var(--text-muted)',
                        marginTop: 'var(--space-xs)',
                    }}
                >
                    {charCount}/{maxChars}
                </div>
            </div>

            <button
                type="submit"
                className="btn btn-primary"
                disabled={submitting || !content.trim()}
                id="create-post-btn"
            >
                {submitting ? '⏳ Posting...' : '🚀 Post'}
            </button>
        </form>
    );
}

export default CreatePostForm;
