import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import API_URL from '../config/api';
import Navigation from './Navigation';

const AdminDashboard = () => {
    const { token } = useAuth();
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const fetchStats = async () => {
        try {
            const response = await axios.get(`${API_URL}/admin/stats`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setStats(response.data);
        } catch (error) {
            console.error('Failed to fetch admin stats:', error);
            if (error.response?.status === 403) {
                alert('Admin access required');
                navigate('/');
            }
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center" style={{ background: '#FFFFFF' }}>
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-gray-200 border-t-black mx-auto mb-4"></div>
                    <p className="text-gray-900 font-medium">Loading admin dashboard...</p>
                </div>
            </div>
        );
    }

    const statCards = [
        {
            label: 'Total Users',
            value: stats?.users.total || 0,
            subtitle: `${stats?.users.verified || 0} verified`,
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
            ),
            color: '#000000',
            bgLight: '#F8F9FA',
        },
        {
            label: 'Banned Users',
            value: stats?.users.banned || 0,
            subtitle: 'accounts restricted',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
                </svg>
            ),
            color: '#333333',
            bgLight: '#F8F9FA',
        },
        {
            label: 'Total Questions',
            value: stats?.questions.total || 0,
            subtitle: 'in question bank',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
            ),
            color: '#666666',
            bgLight: '#F8F9FA',
        },
        {
            label: 'Pending Reports',
            value: stats?.reports.pending || 0,
            subtitle: 'need review',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
            ),
            color: '#555555',
            bgLight: '#F8F9FA',
        },
    ];

    const quickActions = [
        {
            title: 'Manage Users',
            description: 'View, ban, or delete users',
            path: '/admin/users',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
            ),
        },
        {
            title: 'Manage Questions',
            description: 'Upload, edit, or delete questions',
            path: '/admin/questions',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
            ),
        },
        {
            title: 'View Reports',
            description: 'Handle community reports',
            path: '/admin/reports',
            icon: (
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                </svg>
            ),
        },
    ];

    const getActionColor = (actionType) => {
        if (actionType.includes('ban') || actionType.includes('delete')) return '#000000';
        if (actionType.includes('unban') || actionType.includes('create')) return '#333333';
        if (actionType.includes('edit') || actionType.includes('update')) return '#666666';
        return '#000000';
    };

    return (
        <div className="min-h-screen" style={{ background: '#FFFFFF' }}>
            <Navigation />

            <div className="max-w-7xl mx-auto px-4 py-10">
                {/* Header */}
                <div className="mb-10">
                    <div className="flex items-center gap-4 mb-2">
                        <div className="flex items-center justify-center w-12 h-12 rounded-xl" style={{ background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)', boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)' }}>
                            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold" style={{ color: '#1F2937' }}>Admin Dashboard</h1>
                            <p className="text-sm" style={{ color: '#6B7280' }}>Manage users, questions, and community reports</p>
                        </div>
                    </div>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
                    {statCards.map((stat, index) => (
                        <div
                            key={index}
                            className="bg-white rounded-2xl p-6 transition-all duration-300"
                            style={{ boxShadow: '0 2px 12px hsla(0, 0%, 0%, 0.06)' }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-4px)';
                                e.currentTarget.style.boxShadow = '0 12px 24px rgba(0, 0, 0, 0.1)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'translateY(0)';
                                e.currentTarget.style.boxShadow = '0 2px 12px rgba(0, 0, 0, 0.06)';
                            }}
                        >
                            <div className="flex items-start justify-between mb-4">
                                <div
                                    className="flex items-center justify-center w-12 h-12 rounded-xl"
                                    style={{ backgroundColor: stat.bgLight, color: stat.color }}
                                >
                                    {stat.icon}
                                </div>
                            </div>
                            <p className="text-sm font-medium mb-1" style={{ color: '#6B7280' }}>{stat.label}</p>
                            <p className="text-3xl font-bold mb-1" style={{ color: stat.color }}>{stat.value}</p>
                            <p className="text-xs" style={{ color: '#9CA3AF' }}>{stat.subtitle}</p>
                        </div>
                    ))}
                </div>

                {/* Quick Actions */}
                <div className="mb-10">
                    <h2 className="text-lg font-semibold mb-4" style={{ color: '#1F2937' }}>Quick Actions</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                        {quickActions.map((action, index) => (
                            <button
                                key={index}
                                onClick={() => navigate(action.path)}
                                className="group bg-white rounded-2xl p-6 text-left transition-all duration-300 border-2 border-transparent hover:border-gray-300 hover:shadow-lg"
                                style={{ boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)' }}
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-4">
                                        <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-gray-100 text-gray-600 group-hover:bg-gray-200">
                                            {action.icon}
                                        </div>
                                        <div>
                                            <p className="font-semibold text-gray-900">{action.title}</p>
                                            <p className="text-sm text-gray-600">{action.description}</p>
                                        </div>
                                    </div>
                                    <div className="w-8 h-8 rounded-full flex items-center justify-center bg-gray-100 text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
                                        →
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Recent Actions */}
                <div className="bg-white rounded-2xl overflow-hidden" style={{ boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)' }}>
                    <div className="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-gray-100">
                                <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <h2 className="text-lg font-semibold text-gray-900">Recent Admin Actions</h2>
                        </div>
                        <button
                            onClick={() => navigate('/admin/logs')}
                            className="text-sm font-medium px-4 py-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
                        >
                            View All Logs →
                        </button>
                    </div>
                    <div className="p-6">
                        {stats?.recent_actions && stats.recent_actions.length > 0 ? (
                            <div className="space-y-3">
                                {stats.recent_actions.map((action, index) => {
                                    const actionColor = getActionColor(action.action_type);
                                    return (
                                        <div key={index} className="flex items-center justify-between p-4 rounded-xl bg-gray-50">
                                            <div className="flex items-center gap-4">
                                                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: actionColor }}></div>
                                                <div>
                                                    <p className="font-medium text-sm text-gray-900">
                                                        {action.action_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                                                    </p>
                                                    <p className="text-xs text-gray-600">by {action.admin_username}</p>
                                                </div>
                                            </div>
                                            <p className="text-xs font-medium text-gray-500">
                                                {new Date(action.created_at).toLocaleString()}
                                            </p>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="text-center py-12">
                                <div className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center bg-gray-100">
                                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                                    </svg>
                                </div>
                                <p className="font-medium text-gray-600">No recent actions</p>
                                <p className="text-sm text-gray-500">Admin activity will appear here</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
