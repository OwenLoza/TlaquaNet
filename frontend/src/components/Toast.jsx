/**
 * Toast.jsx — Toast Notification Component
 * ==========================================
 * Shows a brief notification at the bottom-right of the screen.
 * Auto-dismisses after 3 seconds with a fade-out animation.
 */

function Toast({ message, type = 'success' }) {
    return (
        <div className={`toast ${type}`} role="alert">
            {message}
        </div>
    );
}

export default Toast;
