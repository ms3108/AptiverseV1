import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';
import { useNavigate } from 'react-router-dom';
import Navigation from './Navigation';

function AdminReports() {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, pending, resolved, rejected
    const navigate = useNavigate();

    useEffect(() => {
        fetchReports();
    }, [filter]);

    const fetchReports = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(
                `${API_URL}/admin/reports?status=${filter === 'all' ? '' : filter}`,
                {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                }
            );

            if (!response.ok) {
                throw new Error('Failed to fetch reports');
            }

            const data = await response.json();
            setReports(data.reports || []);
        } catch (error) {
            console.error('Error fetching reports:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleReportAction = async (reportId, action, actionType = 'no_action') => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(
                `${API_URL}/admin/reports/${reportId}/resolve`,
                {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        action: actionType,
                        ban_permanent: false
                    })
                }
            );

            if (!response.ok) {
                throw new Error(`Failed to ${action} report`);
            }

            // Refresh reports
            fetchReports();
        } catch (error) {
            console.error(`Error ${action} report:`, error);
            alert(`Failed to ${action} report`);
        }
    };

    const getStatusBadge = (status) => {
        const styles = {
            pending: 'bg-yellow-100 text-yellow-800',
            resolved: 'bg-green-100 text-green-800',
            rejected: 'bg-red-100 text-red-800'
        };

        return (
            <span className={`px-3 py-1 rounded-full text-xs font-semibold ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
        );
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Navigation />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Header */}
                <div className="mb-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Community Reports</h1>
                            <p className="text-gray-600 mt-2">Review and manage user-reported content</p>
                        </div>
                        <button
                            onClick={() => navigate('/admin')}
                            className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                        >
                            ← Back to Dashboard
                        </button>
                    </div>
                </div>

                {/* Filters */}
                <div className="bg-white rounded-xl shadow-sm p-6 mb-6">
                    <div className="flex gap-4">
                        {['all', 'pending', 'resolved', 'rejected'].map((status) => (
                            <button
                                key={status}
                                onClick={() => setFilter(status)}
                                className={`px-4 py-2 rounded-lg font-medium transition-colors ${filter === status
                                    ? 'bg-blue-600 text-white'
                                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                    }`}
                            >
                                {status.charAt(0).toUpperCase() + status.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Reports List */}
                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                        <p className="text-gray-600 mt-4">Loading reports...</p>
                    </div>
                ) : reports.length === 0 ? (
                    <div className="bg-white rounded-xl shadow-sm p-12 text-center">
                        <div className="text-6xl mb-4">📭</div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Reports Found</h3>
                        <p className="text-gray-600">
                            {filter === 'all'
                                ? 'No reports have been submitted yet.'
                                : `No ${filter} reports at this time.`
                            }
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {reports.map((report) => (
                            <div key={report.id} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow">
                                <div className="p-6">
                                    {/* Report Header */}
                                    <div className="flex items-start justify-between mb-4">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <h3 className="text-lg font-semibold text-gray-900">
                                                    � Post Report #{report.id}
                                                </h3>
                                                {getStatusBadge(report.status)}
                                            </div>
                                            <div className="flex items-center gap-4 text-sm text-gray-600">
                                                <span>👤 Reported by: <span className="font-medium">{report.reported_by.username}</span></span>
                                                <span>•</span>
                                                <span>📅 {formatDate(report.created_at)}</span>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Report Reason */}
                                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                                        <div className="text-sm font-medium text-gray-700 mb-1">Report Reason:</div>
                                        <div className="text-gray-900">{report.reason}</div>
                                    </div>

                                    {/* Reported Content */}
                                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                                        <div className="text-sm font-medium text-gray-700 mb-2">Reported Content:</div>
                                        <div className="text-gray-900">{report.post_content || 'Content not available'}</div>
                                        {report.posted_by && (
                                            <div className="text-sm text-gray-600 mt-2">
                                                Posted by: <span className="font-medium">{report.posted_by.username}</span> ({report.posted_by.email})
                                            </div>
                                        )}
                                    </div>

                                    {/* Admin Action Section */}
                                    {report.status === 'resolved' ? (
                                        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                                            <div className="text-sm font-medium text-gray-700 mb-1">
                                                Admin Action: Resolved
                                            </div>
                                            <div className="text-gray-900 mb-2">
                                                Action taken: <span className="font-semibold">{report.resolution_action}</span>
                                            </div>
                                            <div className="text-sm text-gray-600">
                                                {report.resolved_at && `Resolved on: ${formatDate(report.resolved_at)}`}
                                            </div>
                                        </div>
                                    ) : (
                                        <div className="space-y-3">
                                            <div className="text-sm font-medium text-gray-700 mb-2">Choose Action:</div>
                                            <div className="grid grid-cols-2 gap-3">
                                                <button
                                                    onClick={() => {
                                                        if (window.confirm('Mark this report as resolved with no action needed?')) {
                                                            handleReportAction(report.id, 'resolve', 'no_action');
                                                        }
                                                    }}
                                                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                                                >
                                                    ✓ No Action Needed
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        if (window.confirm('Warn the user who posted this content?')) {
                                                            handleReportAction(report.id, 'resolve', 'warn_user');
                                                        }
                                                    }}
                                                    className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors font-medium"
                                                >
                                                    ⚠️ Warn User
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        if (window.confirm('Delete this post?')) {
                                                            handleReportAction(report.id, 'resolve', 'delete_post');
                                                        }
                                                    }}
                                                    className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors font-medium"
                                                >
                                                    🗑️ Delete Post
                                                </button>
                                                <button
                                                    onClick={() => {
                                                        if (window.confirm('BAN this user? This is a serious action!')) {
                                                            handleReportAction(report.id, 'resolve', 'ban_user');
                                                        }
                                                    }}
                                                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
                                                >
                                                    🚫 Ban User
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Stats Footer */}
                {!loading && reports.length > 0 && (
                    <div className="mt-6 bg-white rounded-xl shadow-sm p-4">
                        <div className="text-center text-sm text-gray-600">
                            Showing {reports.length} {filter === 'all' ? '' : filter} report{reports.length !== 1 ? 's' : ''}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default AdminReports;

