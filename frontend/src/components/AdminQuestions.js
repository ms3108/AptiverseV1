
import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import API_URL from '../config/api';
import Navigation from './Navigation';

const AdminQuestions = () => {
    const { token } = useAuth();
    const [questions, setQuestions] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(false);
    const [uploadFile, setUploadFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [uploadResult, setUploadResult] = useState(null);

    useEffect(() => {
        fetchQuestions();
    }, []);

    const fetchQuestions = async () => {
        setLoading(true);
        try {
            const response = await axios.get(`${API_URL}/admin/questions`, {
                params: { limit: 100 },
                headers: { Authorization: `Bearer ${token}` }
            });
            setQuestions(response.data.questions);
            setTotal(response.data.total);
        } catch (error) {
            console.error('Failed to fetch questions:', error);
            alert('Failed to load questions');
        } finally {
            setLoading(false);
        }
    };

    const handleFileUpload = async (e) => {
        e.preventDefault();
        if (!uploadFile) {
            alert('Please select a file');
            return;
        }

        setUploading(true);
        setUploadResult(null);

        const formData = new FormData();
        formData.append('file', uploadFile);

        try {
            const response = await axios.post(`${API_URL}/admin/questions/upload`, formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            setUploadResult(response.data);
            setUploadFile(null);
            fetchQuestions();
        } catch (error) {
            console.error('Upload failed:', error);
            alert(error.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const handleDeleteQuestion = async (questionId) => {
        if (!window.confirm('Are you sure you want to delete this question?')) {
            return;
        }

        try {
            await axios.delete(`${API_URL}/admin/questions/${questionId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            alert('Question deleted successfully');
            fetchQuestions();
        } catch (error) {
            console.error('Delete failed:', error);
            alert('Failed to delete question');
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Navigation />

            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-6">
                    <h1 className="text-3xl font-bold text-gray-900">Question Management</h1>
                    <p className="text-gray-600 mt-2">Total Questions: {total}</p>
                </div>

                {/* Upload Section */}
                <div className="bg-white rounded-lg shadow p-6 mb-6">
                    <h2 className="text-xl font-semibold text-gray-900 mb-4">Upload Questions</h2>

                    {/* Format Example */}
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                        <div className="text-sm font-medium text-gray-700 mb-2">JSON Format Example:</div>
                        <pre className="text-xs text-gray-600 overflow-x-auto">
                            {`[
  {
    "question": "If a train runs at 60 km/h for 2 hours, how far does it travel?",
    "options": ["100 km", "120 km", "110 km", "130 km"],
    "answer": "120 km",
    "difficulty": "easy",
    "topic": "quants",
    "subtopic": "speed_distance_time",
    "solution": "Distance = Speed × Time = 60 × 2 = 120 km"
  }
]`}
                        </pre>
                    </div>

                    {/* Upload Form */}
                    <form onSubmit={handleFileUpload} className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Select JSON File
                            </label>
                            <input
                                type="file"
                                accept=".json"
                                onChange={(e) => setUploadFile(e.target.files[0])}
                                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-lg file:border-0
                  file:text-sm file:font-semibold
                  file:bg-indigo-50 file:text-indigo-700
                  hover:file:bg-indigo-100"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={uploading || !uploadFile}
                            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {uploading ? 'Uploading...' : 'Upload Questions'}
                        </button>
                    </form>

                    {/* Upload Result */}
                    {uploadResult && (
                        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                            <div className="font-semibold text-blue-900 mb-2">Upload Results:</div>
                            <div className="text-sm text-blue-800 space-y-1">
                                <div>✅ Total processed: {uploadResult.total}</div>
                                <div>✅ Successfully added: {uploadResult.added}</div>
                                <div>⚠️ Duplicates rejected: {uploadResult.duplicates}</div>
                                {uploadResult.errors && uploadResult.errors.length > 0 && (
                                    <div className="mt-2">
                                        <div className="font-medium text-red-600">Errors:</div>
                                        <ul className="list-disc list-inside text-red-700 text-xs mt-1">
                                            {uploadResult.errors.slice(0, 5).map((error, idx) => (
                                                <li key={idx}>{error}</li>
                                            ))}
                                            {uploadResult.errors.length > 5 && (
                                                <li>... and {uploadResult.errors.length - 5} more errors</li>
                                            )}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                {/* Questions List */}
                <div className="bg-white rounded-lg shadow overflow-hidden">
                    <div className="px-6 py-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">All Questions</h2>
                    </div>

                    {loading ? (
                        <div className="p-8 text-center text-gray-500">Loading questions...</div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Title</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Topic</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difficulty</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {questions.map((question) => (
                                        <tr key={question.id} className="hover:bg-gray-50">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                #{question.id}
                                            </td>
                                            <td className="px-6 py-4 text-sm text-gray-900">
                                                <div className="max-w-md truncate">{question.title}</div>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                <div>{question.topic}</div>
                                                {question.sub_topic && (
                                                    <div className="text-xs text-gray-400">{question.sub_topic}</div>
                                                )}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap">
                                                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${question.difficulty === 'easy' ? 'bg-green-100 text-green-800' :
                                                    question.difficulty === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                                                        'bg-red-100 text-red-800'
                                                    }`}>
                                                    {question.difficulty}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                {new Date(question.created_at).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                <button
                                                    onClick={() => handleDeleteQuestion(question.id)}
                                                    className="text-red-600 hover:text-red-900"
                                                >
                                                    Delete
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminQuestions;
