import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import WarningsModal from './WarningsModal';
import API_URL from '../config/api';

function Navigation() {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const isAdmin = user?.is_admin;
    const [warningsCount, setWarningsCount] = useState(0);
    const [showWarningsModal, setShowWarningsModal] = useState(false);

    useEffect(() => {
        if (!isAdmin && user) {
            fetchWarningsCount();
        }
    }, [user, isAdmin]);

    const fetchWarningsCount = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/warnings`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setWarningsCount(data.unread || 0);
            }
        } catch (error) {
            console.error('Error fetching warnings:', error);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav className="bg-white border-b" style={{ borderColor: '#E2E8F0', boxShadow: '0px 2px 8px rgba(30, 136, 229, 0.06)' }}>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center space-x-4">
                        <h1
                            className="text-2xl font-bold tracking-tight cursor-pointer"
                            onClick={() => navigate(isAdmin ? '/admin' : '/dashboard')}
                            style={{
                                background: 'linear-gradient(135deg, #1E88E5 0%, #1565C0 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                backgroundClip: 'text',
                                letterSpacing: '-0.5px'
                            }}
                        >
                            Aptiverse
                        </h1>
                        {!isAdmin && (
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="px-5 py-2 text-sm font-semibold bg-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                style={{
                                    border: '2px solid #1E88E5',
                                    color: '#1E88E5',
                                    borderRadius: '10px',
                                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                            >
                                🏠 Dashboard
                            </button>
                        )}
                    </div>
                    <div className="flex items-center space-x-4">
                        {!isAdmin && (
                            <>
                                <button
                                    onClick={() => navigate('/practice')}
                                    className="px-6 py-2 text-sm font-semibold hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2 text-white"
                                    style={{
                                        background: 'linear-gradient(135deg, #1E88E5 0%, #42A5F5 100%)',
                                        borderRadius: '10px',
                                        boxShadow: '0px 4px 10px rgba(30, 136, 229, 0.3)',
                                        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                    }}
                                >
                                    Today's Practice Set
                                </button>
                                <button
                                    onClick={() => {
                                        // Clear any existing query parameters and navigate to main category page
                                        navigate('/question-bank', { replace: true });
                                        window.location.href = '/question-bank';
                                    }}
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
                                        border: '2px solid #0D47A1',
                                        color: '#0D47A1',
                                        borderRadius: '10px',
                                        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                    }}
                                >
                                    ⚔️ Battles
                                </button>
                            </>
                        )}
                        {isAdmin && (
                            <>
                                <button
                                    onClick={() => navigate('/admin')}
                                    className="px-4 py-2 text-sm font-semibold text-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                    style={{
                                        background: 'linear-gradient(135deg, #1565C0 0%, #1E88E5 100%)',
                                        borderRadius: '10px',
                                        boxShadow: '0px 4px 10px rgba(21, 101, 192, 0.3)',
                                        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                    }}
                                >
                                    👑 Admin Dashboard
                                </button>
                                <button
                                    onClick={() => navigate('/admin/users')}
                                    className="px-4 py-2 text-sm font-semibold bg-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                    style={{
                                        border: '2px solid #1E88E5',
                                        color: '#1E88E5',
                                        borderRadius: '10px',
                                        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                    }}
                                >
                                    👥 Users
                                </button>
                                <button
                                    onClick={() => navigate('/admin/questions')}
                                    className="px-4 py-2 text-sm font-semibold bg-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                    style={{
                                        border: '2px solid #42A5F5',
                                        color: '#42A5F5',
                                        borderRadius: '10px',
                                        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                    }}
                                >
                                    📝 Questions
                                </button>
                            </>
                        )}
                        {!isAdmin && warningsCount > 0 && (
                            <button
                                onClick={() => setShowWarningsModal(true)}
                                className="relative px-4 py-2 text-sm font-semibold hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                style={{
                                    border: '2px solid #1565C0',
                                    color: '#1565C0',
                                    borderRadius: '10px',
                                    transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                }}
                            >
                                ⚠️ Warnings
                                {warningsCount > 0 && (
                                    <span className="absolute -top-2 -right-2 bg-blue-600 text-white text-xs font-bold rounded-full h-6 w-6 flex items-center justify-center animate-pulse">
                                        {warningsCount}
                                    </span>
                                )}
                            </button>
                        )}
                        <span className="text-sm" style={{ color: '#64748B', letterSpacing: '0.3px' }}>
                            Welcome, <span className="font-semibold" style={{ color: '#1E88E5' }}>{user?.username}</span>!
                        </span>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 text-sm font-semibold text-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                            style={{
                                backgroundColor: '#1565C0',
                                borderRadius: '10px',
                                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                            }}
                        >
                            Logout
                        </button>
                    </div>
                </div>
            </div>
            <WarningsModal
                isOpen={showWarningsModal}
                onClose={() => {
                    setShowWarningsModal(false);
                    fetchWarningsCount(); // Refresh count after closing
                }}
            />
        </nav>
    );
}

export default Navigation;
