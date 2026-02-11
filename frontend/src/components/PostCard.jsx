/**
 * PostCard.jsx — Post Display Component
 * =======================================
 * Renders a single post with:
 * - Author info & avatar
 * - Post content
 * - Like button with count
 * - Expandable comments section
 */

import { useState } from 'react';
import { likePost, unlikePost, createComment } from '../api.js';

function PostCard({ post, currentUser, onUpdated, onError, showToast }) {
    const [showComments, setShowComments] = useState(false);
    const [commentText, setCommentText] = useState('');
    const [submittingComment, setSubmittingComment] = useState(false);
    const [likeAnimating, setLikeAnimating] = useState(false);

    // Check if current user has liked this post
    const isLiked = currentUser && post.liked_by.includes(currentUser.id);

    // Format timestamp to relative time
    const formatTime = (dateStr) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000);

        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    // ── Like / Unlike ──────────────────────────────────────────
    const handleLike = async () => {
        if (!currentUser) {
            onError('Select a user first to like posts');
            return;
        }

        setLikeAnimating(true);
        setTimeout(() => setLikeAnimating(false), 300);

        try {
            if (isLiked) {
                await unlikePost(post.id, currentUser.id);
            } else {
                await likePost(post.id, currentUser.id);
            }
            onUpdated();
        } catch (err) {
            onError(err.message);
        }
    };

    // ── Comment ────────────────────────────────────────────────
    const handleComment = async (e) => {
        e.preventDefault();
        if (!commentText.trim() || !currentUser) return;

        setSubmittingComment(true);
        try {
            await createComment(post.id, commentText.trim(), currentUser.id);
            setCommentText('');
            onUpdated();
            showToast('Comment added! 💬');
        } catch (err) {
            onError(err.message);
        } finally {
            setSubmittingComment(false);
        }
    };

    // Get author info (from nested author object or fallback)
    const authorName = post.author?.display_name || `User #${post.author_id}`;
    const authorUsername = post.author?.username || `user${post.author_id}`;
    const authorInitial = authorName.charAt(0).toUpperCase();

    return (
        <div className="card post-card" id={`post-${post.id}`}>
            {/* Post Header */}
            <div className="post-header">
                <div className="post-avatar">{authorInitial}</div>
                <div className="post-author-info">
                    <div className="post-display-name">{authorName}</div>
                    <div className="post-username">@{authorUsername}</div>
                </div>
                <span className="post-timestamp">{formatTime(post.created_at)}</span>
            </div>

            {/* Post Content */}
            <div className="post-content">{post.content}</div>

            {/* Actions: Like & Comment */}
            <div className="post-actions">
                <button
                    className={`btn btn-like ${isLiked ? 'liked' : ''} ${likeAnimating ? 'like-pulse' : ''}`}
                    onClick={handleLike}
                    id={`like-btn-${post.id}`}
                >
                    {isLiked ? '❤️' : '🤍'} {post.like_count}
                </button>

                <button
                    className="btn btn-ghost"
                    onClick={() => setShowComments(!showComments)}
                    id={`comments-toggle-${post.id}`}
                >
                    💬 {post.comment_count}
                </button>
            </div>

            {/* Comments Section */}
            {showComments && (
                <div className="comments-section">
                    {/* Existing Comments */}
                    {post.comments && post.comments.length > 0 ? (
                        post.comments.map((comment) => (
                            <div className="comment-item" key={comment.id}>
                                <div className="comment-avatar">
                                    {(comment.author?.display_name || 'U').charAt(0).toUpperCase()}
                                </div>
                                <div className="comment-body">
                                    <span className="comment-author">
                                        {comment.author?.display_name || `User #${comment.author_id}`}
                                    </span>{' '}
                                    <span className="comment-text">{comment.content}</span>
                                    <div className="comment-time">{formatTime(comment.created_at)}</div>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p style={{ color: 'var(--text-muted)', fontSize: 'var(--font-size-sm)' }}>
                            No comments yet. Be the first!
                        </p>
                    )}

                    {/* New Comment Form */}
                    {currentUser && (
                        <form className="comment-form" onSubmit={handleComment}>
                            <input
                                type="text"
                                placeholder="Write a comment..."
                                value={commentText}
                                onChange={(e) => setCommentText(e.target.value)}
                                maxLength={300}
                                id={`comment-input-${post.id}`}
                            />
                            <button
                                type="submit"
                                className="btn btn-primary"
                                disabled={submittingComment || !commentText.trim()}
                                id={`comment-submit-${post.id}`}
                            >
                                {submittingComment ? '...' : '→'}
                            </button>
                        </form>
                    )}
                </div>
            )}
        </div>
    );
}

export default PostCard;
