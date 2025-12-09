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
            const response = await fetch(`${API_URL}/warnings`, {
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
        <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #F0F4FA 0%, #E8F0FE 100%)' }}>
            <nav className="glass" style={{
                borderBottom: '1px solid rgba(226, 232, 240, 0.8)',
                position: 'sticky',
                top: 0,
                zIndex: 50
            }}>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center space-x-4">
                            <h1 className="text-2xl font-extrabold tracking-tight cursor-pointer"
                                onClick={() => navigate('/dashboard')}
                                style={{
                                    background: 'linear-gradient(135deg, #1565C0 0%, #1E88E5 100%)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                    backgroundClip: 'text',
                                    letterSpacing: '-0.5px'
                                }}>
                                Aptiverse
                            </h1>
                        </div>
                        <div className="flex items-center space-x-3">
                            <button
                                onClick={handleStartPractice}
                                className="px-5 py-2.5 text-sm font-semibold text-white rounded-xl transition-all duration-300"
                                style={{
                                    background: 'linear-gradient(135deg, #1E88E5 0%, #1565C0 100%)',
                                    boxShadow: '0 4px 14px rgba(30, 136, 229, 0.4)'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.transform = 'translateY(-2px)';
                                    e.target.style.boxShadow = '0 6px 20px rgba(30, 136, 229, 0.5)';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.transform = 'translateY(0)';
                                    e.target.style.boxShadow = '0 4px 14px rgba(30, 136, 229, 0.4)';
                                }}
                            >
                                🎯 Practice
                            </button>
                            <button
                                onClick={handleQuestionBank}
                                className="px-5 py-2.5 text-sm font-semibold rounded-xl transition-all duration-300"
                                style={{
                                    background: 'white',
                                    color: '#1E88E5',
                                    border: '2px solid #1E88E5'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.background = '#1E88E5';
                                    e.target.style.color = 'white';
                                    e.target.style.transform = 'translateY(-2px)';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.background = 'white';
                                    e.target.style.color = '#1E88E5';
                                    e.target.style.transform = 'translateY(0)';
                                }}
                            >
                                📚 Questions
                            </button>
                            <button
                                onClick={() => navigate('/battle/history')}
                                className="px-5 py-2.5 text-sm font-semibold rounded-xl transition-all duration-300"
                                style={{
                                    background: 'white',
                                    color: '#0D47A1',
                                    border: '2px solid #0D47A1'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.background = '#0D47A1';
                                    e.target.style.color = 'white';
                                    e.target.style.transform = 'translateY(-2px)';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.background = 'white';
                                    e.target.style.color = '#0D47A1';
                                    e.target.style.transform = 'translateY(0)';
                                }}
                            >
                                ⚔️ Battles
                            </button>

                            {/* Notification Bell */}
                            <button
                                onClick={() => setShowNotifications(!showNotifications)}
                                className="relative p-2.5 rounded-xl transition-all duration-300"
                                style={{
                                    background: showNotifications ? 'rgba(30, 136, 229, 0.1)' : 'white',
                                    border: '2px solid #E2E8F0'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.borderColor = '#1E88E5';
                                    e.target.style.background = 'rgba(30, 136, 229, 0.05)';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.borderColor = '#E2E8F0';
                                    e.target.style.background = showNotifications ? 'rgba(30, 136, 229, 0.1)' : 'white';
                                }}
                            >
                                <svg
                                    xmlns="http://www.w3.org/2000/svg"
                                    className="h-5 w-5"
                                    fill="none"
                                    viewBox="0 0 24 24"
                                    stroke="#1E88E5"
                                    strokeWidth={2}
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                                    />
                                </svg>
                                {notificationCount > 0 && (
                                    <span className="absolute -top-1 -right-1 inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white rounded-full animate-pulse" style={{
                                        background: 'linear-gradient(135deg, #1E88E5, #1565C0)'
                                    }}>
                                        {notificationCount > 9 ? '9+' : notificationCount}
                                    </span>
                                )}
                            </button>

                            {/* User info & Logout */}
                            <div className="flex items-center space-x-3 pl-2 border-l-2" style={{ borderColor: '#E2E8F0' }}>
                                <div className="flex items-center px-3 py-1.5 rounded-lg" style={{ background: 'rgba(30, 136, 229, 0.08)' }}>
                                    <span className="text-sm font-medium" style={{ color: '#64748B' }}>
                                        👋 <span className="font-semibold" style={{ color: '#1E88E5' }}>{user?.username}</span>
                                    </span>
                                </div>
                                <button
                                    onClick={handleLogout}
                                    className="px-4 py-2 text-sm font-semibold rounded-xl transition-all duration-300"
                                    style={{
                                        background: '#1565C0',
                                        color: 'white'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.target.style.background = '#0D47A1';
                                        e.target.style.transform = 'translateY(-1px)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.target.style.background = '#1565C0';
                                        e.target.style.transform = 'translateY(0)';
                                    }}
                                >
                                    Logout
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto py-8 sm:px-6 lg:px-8">
                <div className="px-4 sm:px-0 animate-fadeIn">
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

