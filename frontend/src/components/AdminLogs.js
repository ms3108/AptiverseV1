import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const AdminLogs = () => {
    const { token } = useAuth();
    const navigate = useNavigate();
    const [logs, setLogs] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [filters, setFilters] = useState({
        action_type: '',
        admin_id: '',
        skip: 0,
        limit: 50
    });

    useEffect(() => {
        fetchLogs();
    }, [filters]);

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const params = {};
            if (filters.action_type) params.action_type = filters.action_type;
            if (filters.admin_id) params.admin_id = filters.admin_id;
            params.skip = filters.skip;
            params.limit = filters.limit;

            const response = await axios.get(`${API_URL}/admin/logs`, {
                params,
                headers: { Authorization: `Bearer ${token}` }
            });
            setLogs(response.data.logs);
            setTotal(response.data.total);
        } catch (error) {
            console.error('Failed to fetch logs:', error);
            if (error.response?.status === 403) {
                alert('Admin access required');
                navigate('/admin');
            } else {
                alert('Failed to load action logs');
            }
        } finally {
            setLoading(false);
        }
    };

    const formatActionType = (actionType) => {
        return actionType
            .split('_')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    };

    const getActionColor = (actionType) => {
        if (actionType.includes('delete')) return 'text-red-600';
        if (actionType.includes('ban')) return 'text-orange-600';
        if (actionType.includes('unban')) return 'text-green-600';
        if (actionType.includes('upload') || actionType.includes('push')) return 'text-blue-600';
        if (actionType.includes('update') || actionType.includes('edit')) return 'text-yellow-600';
        return 'text-gray-600';
    };

    const actionTypes = [
        'ban_user',
        'ban_user_permanent',
        'unban_user',
        'remove_permanent_ban',
        'reset_password',
        'delete_user',
        'upload_questions',
        'update_question',
        'delete_question',
        'resolve_report'
    ];

    return (
        <div className="min-h-screen bg-gray-50 py-8">
            <div className="max-w-7xl mx-auto px-4">
                {/* Header */}
                <div className="mb-6 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Admin Action Logs</h1>
                        <p className="text-gray-600 mt-2">Total Actions: {total}</p>
                    </div>
                    <button
                        onClick={() => navigate('/admin')}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                        ← Back to Dashboard
                    </button>
                </div>

                {/* Filters */}
                <div className="bg-white rounded-lg shadow p-4 mb-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Filter by Action Type
                            </label>
                            <select
                                value={filters.action_type}
                                onChange={(e) => setFilters({ ...filters, action_type: e.target.value, skip: 0 })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            >
                                <option value="">All Actions</option>
                                {actionTypes.map(type => (
                                    <option key={type} value={type}>{formatActionType(type)}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Results per page
                            </label>
                            <select
                                value={filters.limit}
                                onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value), skip: 0 })}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            >
                                <option value="25">25</option>
                                <option value="50">50</option>
                                <option value="100">100</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Logs Table */}
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    {loading ? (
                        <div className="p-8 text-center text-gray-500">Loading logs...</div>
                    ) : logs.length === 0 ? (
                        <div className="p-8 text-center text-gray-500">
                            <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <p className="text-lg font-medium">No action logs yet</p>
                            <p className="text-sm text-gray-400 mt-1">Admin actions will appear here once performed</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Admin</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Target</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Details</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date/Time</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {logs.map((log) => (
                                        <tr key={log.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`text-sm font-medium ${getActionColor(log.action_type)}`}>
                                                    {formatActionType(log.action_type)}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="text-sm text-gray-900">{log.admin.username}</div>
                                                <div className="text-xs text-gray-500">{log.admin.email}</div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                {log.target_type && (
                                                    <div>
                                                        <div className="text-sm text-gray-900">
                                                            {log.target_type.charAt(0).toUpperCase() + log.target_type.slice(1)}
                                                        </div>
                                                        {log.target_id && (
                                                            <div className="text-xs text-gray-500">ID: {log.target_id}</div>
                                                        )}
                                                    </div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4">
                                                {log.details && Object.keys(log.details).length > 0 ? (
                                                    <div className="text-sm text-gray-600 max-w-md">
                                                        {Object.entries(log.details).slice(0, 3).map(([key, value]) => (
                                                            <div key={key} className="truncate">
                                                                <span className="font-medium">{key}:</span> {
                                                                    typeof value === 'object'
                                                                        ? JSON.stringify(value).substring(0, 50) + '...'
                                                                        : String(value).substring(0, 50)
                                                                }
                                                            </div>
                                                        ))}
                                                        {Object.keys(log.details).length > 3 && (
                                                            <div className="text-xs text-gray-400 mt-1">
                                                                +{Object.keys(log.details).length - 3} more
                                                            </div>
                                                        )}
                                                    </div>
                                                ) : (
                                                    <span className="text-sm text-gray-400">No details</span>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="text-sm text-gray-900">
                                                    {new Date(log.created_at).toLocaleDateString()}
                                                </div>
                                                <div className="text-xs text-gray-500">
                                                    {new Date(log.created_at).toLocaleTimeString()}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Pagination Info */}
                {logs.length > 0 && (
                    <div className="mt-4 text-sm text-gray-600 text-center">
                        Showing {filters.skip + 1} to {Math.min(filters.skip + filters.limit, total)} of {total} logs
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminLogs;
