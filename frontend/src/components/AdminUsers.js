import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import API_URL from '../config/api';
import Navigation from './Navigation';

const AdminUsers = () => {
    const { token } = useAuth();
    const [users, setUsers] = useState([]);
    const [total, setTotal] = useState(0);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(false);
    const [selectedUser, setSelectedUser] = useState(null);
    const [showModal, setShowModal] = useState(false);
    const [actionType, setActionType] = useState(null);

    useEffect(() => {
        fetchUsers();
    }, [search]);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_URL}/admin/users`, {
                params: { search, limit: 100 },
                headers: { Authorization: `Bearer ${token}` }
            });
            setUsers(response.data.users);
            setTotal(response.data.total);
        } catch (error) {
            console.error('Failed to fetch users:', error);
            alert('Failed to load users');
        } finally {
            setLoading(false);
        }
    };

    const handleAction = (user, action) => {
        setSelectedUser(user);
        setActionType(action);
        setShowModal(true);
    };

    const confirmAction = async () => {
        if (!selectedUser) return;

        try {
            let endpoint = '';
            let method = 'post';
            let successMessage = '';
            let response;

            switch (actionType) {
                case 'ban':
                    endpoint = `${API_URL}/admin/users/${selectedUser.id}/ban`;
                    successMessage = 'User banned successfully';
                    break;
                case 'ban_permanent':
                    endpoint = `${API_URL}/admin/users/${selectedUser.id}/ban`;
                    method = 'post';
                    successMessage = 'User permanently banned';
                    break;
                case 'unban':
                    endpoint = `${API_URL}/admin/users/${selectedUser.id}/unban`;
                    successMessage = 'User unbanned successfully';
                    break;
                case 'delete':
                    endpoint = `${API_URL}/admin/users/${selectedUser.id}`;
                    method = 'delete';
                    successMessage = 'User deleted successfully';
                    break;
                case 'reset_password':
                    endpoint = `${API_URL}/admin/users/${selectedUser.id}/reset-password`;
                    successMessage = 'Password reset successfully';
                    break;
                default:
                    return;
            }

            const config = { headers: { Authorization: `Bearer ${token}` } };

            if (actionType === 'ban_permanent') {
                response = await axios.post(endpoint, { permanent: true, reason: 'Banned by admin' }, config);
            } else if (method === 'delete') {
                response = await axios.delete(endpoint, config);
            } else {
                response = await axios.post(endpoint, {}, config);
            }

            // Show appropriate success message
            if (actionType === 'reset_password' && response.data.new_password) {
                alert(`Password reset successfully!\n\nNew password: ${response.data.new_password}\n\nPlease send this to the user.`);
            } else {
                alert(successMessage);
            }

            // Close modal and refresh
            setShowModal(false);
            setSelectedUser(null);
            await fetchUsers();

        } catch (error) {
            console.error('Action failed:', error);
            console.error('Error details:', error.response);

            let errorMessage = 'Action failed';
            if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            } else if (error.message) {
                errorMessage = error.message;
            }

            alert(errorMessage);

            // Close modal even on error
            setShowModal(false);
            setSelectedUser(null);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Navigation />

            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
                    <p className="text-gray-600 mt-2">Total Users: {total}</p>
                </div>

                {/* Search */}
                <div className="mb-6">
                    <input
                        type="text"
                        placeholder="Search by username or email..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                </div>

                {/* Users Table */}
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    {loading ? (
                        <div className="p-8 text-center text-gray-500">Loading users...</div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Stats</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {users.map((user) => (
                                        <tr key={user.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="text-sm font-medium text-gray-900">{user.username}</div>
                                                <div className="text-sm text-gray-500">{user.email}</div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <div className="flex flex-col space-y-1">
                                                    {user.is_admin && (
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                                            Admin
                                                        </span>
                                                    )}
                                                    {user.is_verified ? (
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                                            Verified
                                                        </span>
                                                    ) : (
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                                                            Unverified
                                                        </span>
                                                    )}
                                                    {user.is_permanently_banned && (
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                                                            Permanent Ban
                                                        </span>
                                                    )}
                                                    {user.is_banned && !user.is_permanently_banned && (
                                                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">
                                                            Banned
                                                        </span>
                                                    )}
                                                </div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                <div>Level {user.level} • {user.xp} XP</div>
                                                <div>{user.total_questions_solved} solved</div>
                                                <div>{user.current_streak} day streak</div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {new Date(user.created_at).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                {!user.is_admin && (
                                                    <div className="flex justify-end space-x-2">
                                                        {user.is_banned ? (
                                                            <button
                                                                onClick={() => handleAction(user, 'unban')}
                                                                className="text-green-600 hover:text-green-900"
                                                            >
                                                                Unban
                                                            </button>
                                                        ) : (
                                                            <>
                                                                <button
                                                                    onClick={() => handleAction(user, 'ban')}
                                                                    className="text-orange-600 hover:text-orange-900"
                                                                >
                                                                    Ban
                                                                </button>
                                                                <button
                                                                    onClick={() => handleAction(user, 'ban_permanent')}
                                                                    className="text-red-600 hover:text-red-900"
                                                                >
                                                                    Permanent Ban
                                                                </button>
                                                            </>
                                                        )}
                                                        <button
                                                            onClick={() => handleAction(user, 'reset_password')}
                                                            className="text-blue-600 hover:text-blue-900"
                                                        >
                                                            Reset Password
                                                        </button>
                                                        <button
                                                            onClick={() => handleAction(user, 'delete')}
                                                            className="text-red-600 hover:text-red-900"
                                                        >
                                                            Delete
                                                        </button>
                                                    </div>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                {/* Confirmation Modal */}
                {showModal && (
                    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Confirm Action</h3>
                            <p className="text-gray-600 mb-6">
                                Are you sure you want to {actionType?.replace('_', ' ')} user <strong>{selectedUser?.username}</strong>?
                                {actionType === 'ban_permanent' && (
                                    <span className="block mt-2 text-red-600 font-medium">
                                        This will prevent them from ever registering again with this email!
                                    </span>
                                )}
                            </p>
                            <div className="flex justify-end space-x-3">
                                <button
                                    onClick={() => {
                                        setShowModal(false);
                                        setSelectedUser(null);
                                    }}
                                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={confirmAction}
                                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
                                >
                                    Confirm
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminUsers;
