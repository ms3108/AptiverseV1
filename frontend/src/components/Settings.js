import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';
import { useAuth } from '../context/AuthContext';
import Navigation from './Navigation';
import axios from 'axios';

function Settings() {
    const { token, user } = useAuth();
    const [dailyPracticeCount, setDailyPracticeCount] = useState(10);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        if (token) {
            fetchPreferences();
        }
    }, [token]);

    const fetchPreferences = async () => {
        try {
            const response = await axios.get(`${API_URL}/user/preferences`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setDailyPracticeCount(response.data.daily_practice_count);
            setLoading(false);
        } catch (error) {
            console.error('Error fetching preferences:', error);
            console.error('Token:', token);
            setLoading(false);
        }
    };

    const handleSave = async () => {
        if (!token) {
            setMessage('❌ Authentication error. Please log in again.');
            return;
        }

        setSaving(true);
        setMessage('');

        try {
            const response = await axios.put(
                `${API_URL}/user/preferences?daily_practice_count=${dailyPracticeCount}`,
                {},
                {
                    headers: { Authorization: `Bearer ${token}` }
                }
            );
            setMessage('✅ Settings saved successfully!');
            console.log('Save response:', response.data);
            setTimeout(() => setMessage(''), 3000);
        } catch (error) {
            const errorMsg = error.response?.data?.detail || error.message;
            setMessage(`❌ Error: ${errorMsg}`);
            console.error('Error saving preferences:', error);
            console.error('Token being used:', token);
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <>
                <Navigation />
                <div className="min-h-screen flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #1E88E5 0%, #EC4899 100%)' }}>
                    <div className="text-white text-xl">Loading settings...</div>
                </div>
            </>
        );
    }

    return (
        <>
            <Navigation />
            <div className="min-h-screen py-12 px-4 bg-gray-50">
                <div className="max-w-2xl mx-auto">
                    {/* Header */}
                    <div className="mb-8">
                        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
                        <p className="text-gray-600 mt-1">Manage your practice preferences</p>
                    </div>

                    {/* Settings Card */}
                    <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                        <div className="p-6">
                            {/* Account Section */}
                            <div className="mb-8">
                                <h2 className="text-lg font-semibold text-gray-900 mb-3">
                                    Account
                                </h2>
                                <div className="space-y-2 text-sm">
                                    <div className="flex justify-between py-2">
                                        <span className="text-gray-600">Username</span>
                                        <span className="text-gray-900 font-medium">{user?.username}</span>
                                    </div>
                                    <div className="flex justify-between py-2">
                                        <span className="text-gray-600">Email</span>
                                        <span className="text-gray-900 font-medium">{user?.email}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Divider */}
                            <div className="border-t border-gray-200 my-6"></div>

                            {/* Practice Settings */}
                            <div className="mb-6">
                                <h2 className="text-lg font-semibold text-gray-900 mb-3">
                                    Practice Preferences
                                </h2>

                                <div>
                                    <label className="block text-sm font-medium text-gray-900 mb-2">
                                        Questions per practice set
                                    </label>
                                    <p className="text-sm text-gray-500 mb-4">
                                        Choose how many questions you want in your daily practice
                                    </p>

                                    <div className="flex items-center gap-6">
                                        <input
                                            type="range"
                                            min="5"
                                            max="50"
                                            step="5"
                                            value={dailyPracticeCount}
                                            onChange={(e) => setDailyPracticeCount(parseInt(e.target.value))}
                                            className="flex-1 h-2 rounded-lg appearance-none cursor-pointer"
                                            style={{
                                                background: `linear-gradient(to right, #6366F1 0%, #6366F1 ${((dailyPracticeCount - 5) / 45) * 100}%, #E5E7EB ${((dailyPracticeCount - 5) / 45) * 100}%, #E5E7EB 100%)`
                                            }}
                                        />
                                        <div className="flex items-center gap-2">
                                            <span className="text-2xl font-bold text-gray-900">{dailyPracticeCount}</span>
                                            <span className="text-sm text-gray-500">questions</span>
                                        </div>
                                    </div>

                                    {/* Range markers */}
                                    <div className="flex justify-between text-xs text-gray-400 mt-2 px-1">
                                        <span>5</span>
                                        <span>25</span>
                                        <span>50</span>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Message Display */}
                        {message && (
                            <div className={`mt-6 p-3 rounded-lg text-sm ${message.includes('✅')
                                    ? 'bg-green-50 text-green-700 border border-green-200'
                                    : 'bg-red-50 text-red-700 border border-red-200'
                                }`}>
                                {message}
                            </div>
                        )}

                        {/* Save Button */}
                        <div className="mt-6 pt-6 border-t border-gray-200">
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                className="w-full py-3 rounded-lg text-white font-semibold text-base transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                                style={{
                                    backgroundColor: saving ? '#9CA3AF' : '#6366F1'
                                }}
                                onMouseEnter={(e) => {
                                    if (!saving) e.target.style.backgroundColor = '#4F46E5';
                                }}
                                onMouseLeave={(e) => {
                                    if (!saving) e.target.style.backgroundColor = '#6366F1';
                                }}
                            >
                                {saving ? 'Saving...' : 'Save Changes'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
}

export default Settings;


