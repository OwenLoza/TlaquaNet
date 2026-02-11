/**
 * CreateUserForm.jsx — User Registration Component
 * ==================================================
 * Simple form to create a new user profile.
 * No authentication — just pick a username and display name.
 */

import { useState } from 'react';
import { createUser } from '../api.js';

function CreateUserForm({ onUserCreated, onError }) {
    const [username, setUsername] = useState('');
    const [displayName, setDisplayName] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username.trim() || !displayName.trim()) return;

        setSubmitting(true);
        try {
            const newUser = await createUser(username.trim(), displayName.trim());
            onUserCreated(newUser);
            setUsername('');
            setDisplayName('');
        } catch (err) {
            onError(err.message);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div>
            <div className="section-title">
                <span className="icon">👤</span>
                Create a New Profile
            </div>

            <form className="card" onSubmit={handleSubmit}>
                <div className="form-row">
                    <div className="form-group">
                        <label htmlFor="username">Username</label>
                        <input
                            id="username"
                            className="form-input"
                            type="text"
                            placeholder="e.g. data_ninja"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            minLength={3}
                            maxLength={50}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <label htmlFor="display-name">Display Name</label>
                        <input
                            id="display-name"
                            className="form-input"
                            type="text"
                            placeholder="e.g. Data Ninja 🥷"
                            value={displayName}
                            onChange={(e) => setDisplayName(e.target.value)}
                            maxLength={100}
                            required
                        />
                    </div>
                </div>

                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={submitting || !username.trim() || !displayName.trim()}
                    id="create-user-btn"
                >
                    {submitting ? '⏳ Creating...' : '✨ Create Profile'}
                </button>
            </form>
        </div>
    );
}

export default CreateUserForm;
