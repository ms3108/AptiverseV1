import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';

function NotificationsPanel({ isOpen, onClose, anchorEl }) {
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total: 0, unread: 0 });

    useEffect(() => {
        if (isOpen) {
            fetchNotifications();
        }
    }, [isOpen]);

    const fetchNotifications = async () => {
        try {
            const token = localStorage.getItem('token');

            // Fetch warnings
            const warningsResponse = await fetch(`${API_URL}/warnings`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            // Fetch badges (recent earned badges)
            const statsResponse = await fetch(`${API_URL}/dashboard/stats`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            const allNotifications = [];

            if (warningsResponse.ok) {
                const warningsData = await warningsResponse.json();
                const warningNotifs = warningsData.warnings.map(w => ({
                    id: `warning-${w.id}`,
                    type: 'warning',
                    title: '⚠️ Warning from Admin',
                    message: w.reason,
                    time: w.created_at,
                    isRead: w.is_read,
                    warningId: w.id,
                    priority: 'high'
                }));
                allNotifications.push(...warningNotifs);
            }

            if (statsResponse.ok) {
                const statsData = await statsResponse.json();
                // Get recently earned badges (within last 7 days)
                const recentBadges = statsData.badges
                    ?.filter(b => b.earned_at)
                    .filter(b => {
                        const earnedDate = new Date(b.earned_at);
                        const weekAgo = new Date();
                        weekAgo.setDate(weekAgo.getDate() - 7);
                        return earnedDate > weekAgo;
                    })
                    .map(b => ({
                        id: `badge-${b.name}`,
                        type: 'badge',
                        title: '🎖️ Badge Earned!',
                        message: `You earned the "${b.name}" badge! ${b.description}`,
                        time: b.earned_at,
                        isRead: true, // Badges are auto-read
                        icon: b.icon,
                        priority: 'medium'
                    }));

                if (recentBadges) {
                    allNotifications.push(...recentBadges);
                }
            }

            // Sort by time (newest first)
            allNotifications.sort((a, b) => new Date(b.time) - new Date(a.time));

            setNotifications(allNotifications);
            setStats({
                total: allNotifications.length,
                unread: allNotifications.filter(n => !n.isRead).length
            });
        } catch (error) {
            console.error('Error fetching notifications:', error);
        } finally {
            setLoading(false);
        }
    };

    const markWarningAsRead = async (warningId) => {
        try {
            const token = localStorage.getItem('token');
            await fetch(`${API_URL}/warnings/${warningId}/mark-read`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            // Update local state
            setNotifications(notifications.map(n =>
                n.warningId === warningId ? { ...n, isRead: true } : n
            ));
            setStats(prev => ({
                ...prev,
                unread: Math.max(0, prev.unread - 1)
            }));
        } catch (error) {
            console.error('Error marking warning as read:', error);
        }
    };

    const getTimeAgo = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const seconds = Math.floor((now - date) / 1000);

        if (seconds < 60) return 'Just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        return date.toLocaleDateString();
    };

    const getNotificationStyle = (notification) => {
        if (notification.type === 'warning') {
            return {
                border: '2px solid #F59E0B',
                bg: notification.isRead ? 'bg-orange-50' : 'bg-orange-100'
            };
        }
        return {
            border: '2px solid #10B981',
            bg: 'bg-green-50'
        };
    };

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 z-40"
                onClick={onClose}
            />

            {/* Notifications Panel */}
            <div
                className="fixed right-4 top-20 w-96 bg-white rounded-2xl shadow-2xl z-50 max-h-[600px] flex flex-col"
                style={{
                    border: '2px solid #E2E8F0',
                    animation: 'slideDown 0.3s ease-out'
                }}
            >
                {/* Header */}
                <div className="p-4 border-b border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-lg font-bold text-gray-900">🔔 Notifications</h3>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 p-1 rounded-full hover:bg-gray-100"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                            </svg>
                        </button>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-600">
                        <span>{stats.total} total</span>
                        {stats.unread > 0 && (
                            <>
                                <span>•</span>
                                <span className="font-semibold text-orange-600">{stats.unread} unread</span>
                            </>
                        )}
                    </div>
                </div>

                {/* Notifications List */}
                <div className="flex-1 overflow-y-auto p-2">
                    {loading ? (
                        <div className="text-center py-12">
                            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto"></div>
                            <p className="text-gray-600 mt-3 text-sm">Loading...</p>
                        </div>
                    ) : notifications.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-5xl mb-3">🎉</div>
                            <h4 className="text-lg font-semibold text-gray-900 mb-1">All caught up!</h4>
                            <p className="text-sm text-gray-600">No new notifications</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {notifications.map((notification) => {
                                const style = getNotificationStyle(notification);
                                return (
                                    <div
                                        key={notification.id}
                                        className={`p-4 rounded-xl ${style.bg} transition-all hover:shadow-md`}
                                        style={{ border: style.border }}
                                    >
                                        <div className="flex items-start gap-3">
                                            {/* Icon */}
                                            <div className="flex-shrink-0 text-2xl">
                                                {notification.type === 'badge' ? notification.icon : '⚠️'}
                                            </div>

                                            {/* Content */}
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-start justify-between gap-2 mb-1">
                                                    <h4 className="font-semibold text-gray-900 text-sm">
                                                        {notification.title}
                                                    </h4>
                                                    {!notification.isRead && (
                                                        <span className="flex-shrink-0 w-2 h-2 bg-orange-500 rounded-full mt-1"></span>
                                                    )}
                                                </div>
                                                <p className="text-sm text-gray-700 mb-2 line-clamp-2">
                                                    {notification.message}
                                                </p>
                                                <div className="flex items-center justify-between">
                                                    <span className="text-xs text-gray-500">
                                                        {getTimeAgo(notification.time)}
                                                    </span>
                                                    {notification.type === 'warning' && !notification.isRead && (
                                                        <button
                                                            onClick={() => markWarningAsRead(notification.warningId)}
                                                            className="text-xs font-medium text-orange-600 hover:text-orange-700 px-2 py-1 rounded hover:bg-orange-200 transition-colors"
                                                        >
                                                            Mark as read
                                                        </button>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Footer */}
                {notifications.length > 0 && (
                    <div className="p-3 border-t border-gray-200 bg-gray-50 rounded-b-2xl">
                        <button
                            onClick={() => {
                                onClose();
                                // Could navigate to a full notifications page if needed
                            }}
                            className="w-full text-sm font-medium text-blue-600 hover:text-blue-700 py-2"
                        >
                            View All Notifications
                        </button>
                    </div>
                )}
            </div>

            <style jsx>{`
                @keyframes slideDown {
                    from {
                        opacity: 0;
                        transform: translateY(-10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `}</style>
        </>
    );
}

export default NotificationsPanel;


