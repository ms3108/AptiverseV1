import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardStats from './DashboardStats';
import NotificationsPanel from './NotificationsPanel';

function Dashboard() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [showNotifications, setShowNotifications] = useState(false);
    const [notificationCount, setNotificationCount] = useState(0);

    useEffect(() => {
        fetchNotificationCount();
        // Refresh notification count every 30 seconds
        const interval = setInterval(fetchNotificationCount, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchNotificationCount = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('${API_URL}/warnings', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                setNotificationCount(data.unread || 0);
            }
        } catch (error) {
            console.error('Error fetching notification count:', error);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const handleStartPractice = () => {
        navigate('/practice');
    };

    const handleQuestionBank = () => {
        navigate('/question-bank');
    };

    return (
        <div className="min-h-screen" style={{ backgroundColor: '#F8FAFF' }}>
            <nav className="bg-white border-b" style={{ borderColor: '#E2E8F0', boxShadow: '0px 2px 8px rgba(30, 136, 229, 0.06)' }}>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center space-x-4">
                            <h1 className="text-2xl font-bold tracking-tight" style={{
                                background: 'linear-gradient(135deg, #1E88E5 0%, #EC4899 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                backgroundClip: 'text',
                                letterSpacing: '-0.5px'
                            }}>
                                Aptiverse
                            </h1>
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="px-5 py-2 text-sm font-semibold bg-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                style={{
                                    border: '2px solid #6366F1',
                                    color: '#6366F1',
                                    borderRadius: '10px',
                                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                            >
                                🏠 Dashboard
                            </button>
                        </div>
                        <div className="flex items-center space-x-4">
                            <button
                                onClick={handleStartPractice}
                                className="px-6 py-2 text-sm font-semibold hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2 text-white"
                                style={{
                                    background: 'linear-gradient(135deg, #EC4899 0%, #F472B6 100%)',
                                    borderRadius: '10px',
                                    boxShadow: '0px 4px 10px rgba(236, 72, 153, 0.3)',
                                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                            >
                                Today's Practice Set
                            </button>
                            <button
                                onClick={handleQuestionBank}
                                className="px-6 py-2 text-sm font-semibold bg-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                style={{
                                    border: '2px solid #1E88E5',
                                    color: '#1E88E5',
                                    borderRadius: '10px',
                                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                            >
                                Question Bank
                            </button>
                            <button
                                onClick={() => navigate('/battle/history')}
                                className="px-6 py-2 text-sm font-semibold bg-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                style={{
                                    border: '2px solid #EC4899',
                                    color: '#EC4899',
                                    borderRadius: '10px',
                                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                            >
                                ⚔️ Battles
                            </button>

                            {/* Notification Bell */}
                            <button
                                onClick={() => setShowNotifications(!showNotifications)}
                                className="relative p-2 rounded-full hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-indigo-500"
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-6 w-6 text-gray-600"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="currentColor"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth={2}
                                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                                    />
                                </svg>
                                {notificationCount > 0 && (
                                    <span className="absolute top-0 right-0 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full animate-pulse">
                                        {notificationCount > 9 ? '9+' : notificationCount}
                                    </span>
                                )}
                            </button>

                            <span className="text-sm" style={{ color: '#64748B', letterSpacing: '0.3px' }}>
                                Welcome, <span className="font-semibold" style={{ color: '#1E88E5' }}>{user?.username}</span>!
                            </span>
                            <button
                                onClick={handleLogout}
                                className="px-4 py-2 text-sm font-semibold text-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                style={{
                                    backgroundColor: '#DC2626',
                                    borderRadius: '10px',
                                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
                <div className="px-4 py-6 sm:px-0">
                    <DashboardStats />
                </div>
            </main>

            {/* Notifications Panel */}
            <NotificationsPanel
                isOpen={showNotifications}
                onClose={() => {
                    setShowNotifications(false);
                    fetchNotificationCount(); // Refresh count when closing
                }}
            />
        </div>
    );
}

export default Dashboard;

