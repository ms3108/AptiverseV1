import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navigation() {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const isAdmin = user?.is_admin;

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
                                background: 'linear-gradient(135deg, #1E88E5 0%, #EC4899 100%)',
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
                                    border: '2px solid #6366F1',
                                    color: '#6366F1',
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
                                        background: 'linear-gradient(135deg, #EC4899 0%, #F472B6 100%)',
                                        borderRadius: '10px',
                                        boxShadow: '0px 4px 10px rgba(236, 72, 153, 0.3)',
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
                                        border: '2px solid #EC4899',
                                        color: '#EC4899',
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
                                        background: 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%)',
                                        borderRadius: '10px',
                                        boxShadow: '0px 4px 10px rgba(139, 92, 246, 0.3)',
                                        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                    }}
                                >
                                    👑 Admin Dashboard
                                </button>
                                <button
                                    onClick={() => navigate('/admin/users')}
                                    className="px-4 py-2 text-sm font-semibold bg-white hover-scale focus:outline-none focus:ring-2 focus:ring-offset-2"
                                    style={{
                                        border: '2px solid #8B5CF6',
                                        color: '#8B5CF6',
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
                                        border: '2px solid #10B981',
                                        color: '#10B981',
                                        borderRadius: '10px',
                                        transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
                                    }}
                                >
                                    📝 Questions
                                </button>
                            </>
                        )}
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
    );
}

export default Navigation;
