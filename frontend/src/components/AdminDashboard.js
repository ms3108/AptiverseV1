import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import API_URL from '../config/api';
import Navigation from './Navigation';

const AdminDashboard = () => {
    const { token, logout } = useAuth();
    const navigate = useNavigate();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

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
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-xl">Loading admin dashboard...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            <Navigation />

            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                    <p className="text-gray-600 mt-2">Manage users, questions, and community reports</p>
                </div>

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm font-medium text-gray-500">Total Users</div>
                        <div className="text-3xl font-bold text-gray-900 mt-2">{stats?.users.total || 0}</div>
                        <div className="text-sm text-gray-600 mt-1">
                            {stats?.users.verified || 0} verified
                        </div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm font-medium text-gray-500">Banned Users</div>
                        <div className="text-3xl font-bold text-red-600 mt-2">{stats?.users.banned || 0}</div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm font-medium text-gray-500">Total Questions</div>
                        <div className="text-3xl font-bold text-gray-900 mt-2">{stats?.questions.total || 0}</div>
                    </div>

                    <div className="bg-white rounded-lg shadow p-6">
                        <div className="text-sm font-medium text-gray-500">Pending Reports</div>
                        <div className="text-3xl font-bold text-yellow-600 mt-2">{stats?.reports.pending || 0}</div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <button
                        onClick={() => navigate('/admin/users')}
                        className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition text-left"
                    >
                        <div className="flex items-center">
                            <div className="bg-blue-100 rounded-lg p-3">
                                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                                </svg>
                            </div>
                            <div className="ml-4">
                                <div className="text-lg font-semibold text-gray-900">Manage Users</div>
                                <div className="text-sm text-gray-600">View, ban, or delete users</div>
                            </div>
                        </div>
                    </button>

                    <button
                        onClick={() => navigate('/admin/questions')}
                        className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition text-left"
                    >
                        <div className="flex items-center">
                            <div className="bg-green-100 rounded-lg p-3">
                                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                            </div>
                            <div className="ml-4">
                                <div className="text-lg font-semibold text-gray-900">Manage Questions</div>
                                <div className="text-sm text-gray-600">Upload, edit, or delete questions</div>
                            </div>
                        </div>
                    </button>

                    <button
                        onClick={() => navigate('/admin/reports')}
                        className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition text-left"
                    >
                        <div className="flex items-center">
                            <div className="bg-yellow-100 rounded-lg p-3">
                                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                </svg>
                            </div>
                            <div className="ml-4">
                                <div className="text-lg font-semibold text-gray-900">View Reports</div>
                                <div className="text-sm text-gray-600">Handle community reports</div>
                            </div>
                        </div>
                    </button>
                </div>

                {/* Recent Actions */}
                <div className="bg-white rounded-lg shadow">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">Recent Admin Actions</h2>
                    </div>
                    <div className="p-6">
                        {stats?.recent_actions && stats.recent_actions.length > 0 ? (
                            <div className="space-y-3">
                                {stats.recent_actions.map((action, index) => (
                                    <div key={index} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                            <div>
                                                <div className="text-sm font-medium text-gray-900">
                                                    {action.action_type.replace(/_/g, ' ').toUpperCase()}
                                                </div>
                                                <div className="text-xs text-gray-500">by {action.admin_username}</div>
                                            </div>
                                        </div>
                                        <div className="text-xs text-gray-500">
                                            {new Date(action.created_at).toLocaleString()}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center text-gray-500 py-8">No recent actions</div>
                        )}
                    </div>
                </div>

                {/* Action Logs Link */}
                <div className="mt-6">
                    <button
                        onClick={() => navigate('/admin/logs')}
                        className="text-indigo-600 hover:text-indigo-800 font-medium text-sm"
                    >
                        View All Action Logs →
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AdminDashboard;
