import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';

function WarningsModal({ isOpen, onClose }) {
    const [warnings, setWarnings] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (isOpen) {
            fetchWarnings();
        }
    }, [isOpen]);

    const fetchWarnings = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch('${API_URL}/warnings', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setWarnings(data.warnings || []);
            }
        } catch (error) {
            console.error('Error fetching warnings:', error);
        } finally {
            setLoading(false);
        }
    };

    const markAsRead = async (warningId) => {
        try {
            const token = localStorage.getItem('token');
            await fetch(`${API_URL}/warnings/${warningId}/mark-read`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            // Update local state
            setWarnings(warnings.map(w =>
                w.id === warningId ? { ...w, is_read: true } : w
            ));
        } catch (error) {
            console.error('Error marking warning as read:', error);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-2xl">
                {/* Header */}
                <div className="bg-gradient-to-r from-yellow-500 to-orange-500 px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <span className="text-3xl">⚠️</span>
                        <h2 className="text-2xl font-bold text-white">Your Warnings</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-white hover:bg-white hover:bg-opacity-20 rounded-full p-2 transition-colors"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                {/* Content */}
                <div className="p-6 overflow-y-auto max-h-[calc(80vh-100px)]">
                    {loading ? (
                        <div className="text-center py-8">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-600 mx-auto"></div>
                            <p className="text-gray-600 mt-4">Loading warnings...</p>
                        </div>
                    ) : warnings.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-6xl mb-4">✨</div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">No Warnings</h3>
                            <p className="text-gray-600">You're doing great! Keep following the community guidelines.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {warnings.map((warning) => (
                                <div
                                    key={warning.id}
                                    className={`border rounded-xl p-5 transition-all ${warning.is_read
                                            ? 'bg-gray-50 border-gray-200'
                                            : 'bg-yellow-50 border-yellow-300 shadow-md'
                                        }`}
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center gap-2">
                                            <span className="text-2xl">⚠️</span>
                                            <div>
                                                <div className="font-semibold text-gray-900">
                                                    Community Guidelines Violation
                                                </div>
                                                <div className="text-sm text-gray-600">
                                                    Issued by {warning.issued_by} • {new Date(warning.created_at).toLocaleDateString()}
                                                </div>
                                            </div>
                                        </div>
                                        {!warning.is_read && (
                                            <span className="px-3 py-1 bg-yellow-500 text-white text-xs font-semibold rounded-full">
                                                NEW
                                            </span>
                                        )}
                                    </div>

                                    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-3">
                                        <div className="text-sm font-medium text-gray-700 mb-1">Reason:</div>
                                        <div className="text-gray-900">{warning.reason}</div>
                                    </div>

                                    {!warning.is_read && (
                                        <button
                                            onClick={() => markAsRead(warning.id)}
                                            className="w-full px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors font-medium"
                                        >
                                            Mark as Read
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {/* Important Notice */}
                    {warnings.length > 0 && (
                        <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
                            <div className="flex gap-3">
                                <span className="text-red-600 text-xl">⚠️</span>
                                <div className="flex-1">
                                    <div className="font-semibold text-red-900 mb-1">Important Notice</div>
                                    <p className="text-sm text-red-800">
                                        Multiple violations of community guidelines may result in temporary or permanent account suspension.
                                        Please review our <span className="font-semibold">Community Guidelines</span> to avoid future warnings.
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="bg-gray-50 px-6 py-4 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}

export default WarningsModal;

