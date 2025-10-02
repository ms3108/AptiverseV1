import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardStats from './DashboardStats';

function Dashboard() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

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
        </div>
    );
}

export default Dashboard;
