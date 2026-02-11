/**
 * AnalyticsPanel.jsx — Analytics Dashboard Component
 * ====================================================
 * Shows aggregate statistics from the events table.
 * This is the "data engineering" showcase:
 * students can see how their actions become data points.
 */

function AnalyticsPanel({ summary }) {
    if (!summary) {
        return (
            <div className="empty-state">
                <div className="empty-icon">📊</div>
                <p>Loading analytics...</p>
            </div>
        );
    }

    const stats = [
        {
            label: 'Users Created',
            value: summary.user_created || 0,
            emoji: '👤',
        },
        {
            label: 'Posts Created',
            value: summary.post_created || 0,
            emoji: '📝',
        },
        {
            label: 'Likes Given',
            value: summary.post_liked || 0,
            emoji: '❤️',
        },
        {
            label: 'Comments Made',
            value: summary.comment_created || 0,
            emoji: '💬',
        },
        {
            label: 'Total Events',
            value: summary.total_events || 0,
            emoji: '📊',
        },
    ];

    return (
        <div>
            <div className="section-title">
                <span className="icon">📊</span>
                Platform Analytics
            </div>

            <div className="analytics-grid">
                {stats.map((stat) => (
                    <div className="analytics-stat" key={stat.label} id={`stat-${stat.label.toLowerCase().replace(/\s+/g, '-')}`}>
                        <div style={{ fontSize: '1.5rem', marginBottom: 'var(--space-xs)' }}>
                            {stat.emoji}
                        </div>
                        <div className="stat-value">{stat.value}</div>
                        <div className="stat-label">{stat.label}</div>
                    </div>
                ))}
            </div>

            {/* Info card explaining the analytics design */}
            <div className="card" style={{ borderLeft: '3px solid var(--accent-primary)' }}>
                <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 600, marginBottom: 'var(--space-sm)' }}>
                    🎓 How this works (Data Engineering Notes)
                </h3>
                <ul style={{
                    color: 'var(--text-secondary)',
                    fontSize: 'var(--font-size-sm)',
                    lineHeight: 1.8,
                    paddingLeft: 'var(--space-lg)',
                }}>
                    <li>
                        Every action (create user, post, like, comment) is logged in the <code>events</code> table.
                    </li>
                    <li>
                        Each event has a <strong>type</strong>, <strong>user_id</strong>, <strong>target_id</strong>,
                        and <strong>timestamp</strong>.
                    </li>
                    <li>
                        This is an <strong>append-only event log</strong> — the foundation for event sourcing.
                    </li>
                    <li>
                        In a real pipeline, you'd consume these events with Kafka, transform with dbt,
                        and load into a data warehouse.
                    </li>
                    <li>
                        The SQL schema includes example analytics queries — check <code>sql/schema.sql</code>!
                    </li>
                </ul>
            </div>

            {/* API endpoints reference */}
            <div className="card" style={{ marginTop: 'var(--space-md)' }}>
                <h3 style={{ fontSize: 'var(--font-size-base)', fontWeight: 600, marginBottom: 'var(--space-sm)' }}>
                    🔗 API Endpoints for Analytics
                </h3>
                <div style={{ color: 'var(--text-secondary)', fontSize: 'var(--font-size-sm)', lineHeight: 2 }}>
                    <div><code style={{ color: 'var(--success-color)' }}>GET</code> <code>/api/analytics/events</code> — Raw event log</div>
                    <div><code style={{ color: 'var(--success-color)' }}>GET</code> <code>/api/analytics/events?event_type=post_liked</code> — Filter by type</div>
                    <div><code style={{ color: 'var(--success-color)' }}>GET</code> <code>/api/analytics/summary</code> — Aggregate counts</div>
                    <div><code style={{ color: 'var(--warning-color)' }}>DOCS</code> <code>/docs</code> — Interactive Swagger documentation</div>
                </div>
            </div>
        </div>
    );
}

export default AnalyticsPanel;
