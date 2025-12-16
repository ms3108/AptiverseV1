
import React, { useState, useEffect, useCallback } from 'react';
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
    const [bulkText, setBulkText] = useState('');
    const [textUploading, setTextUploading] = useState(false);
    const [activeUploadTab, setActiveUploadTab] = useState('file'); // 'file' or 'text'

    // Search and filter state
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedDifficulty, setSelectedDifficulty] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [topics, setTopics] = useState([]);

    const fetchQuestions = useCallback(async () => {
        setLoading(true);
        try {
            const params = { limit: 100 };
            if (searchQuery) params.search = searchQuery;
            if (selectedCategory) params.category = selectedCategory;
            if (selectedDifficulty) params.difficulty = selectedDifficulty;
            if (selectedTopic) params.topic = selectedTopic;

            const response = await axios.get(`${API_URL}/admin/questions`, {
                params,
                headers: { Authorization: `Bearer ${token}` }
            });
            setQuestions(response.data.questions);
            setTotal(response.data.total);

            // Extract unique topics from questions for filter dropdown
            if (!selectedCategory && !selectedDifficulty && !searchQuery && !selectedTopic) {
                const uniqueTopics = [...new Set(response.data.questions.map(q => q.topic).filter(Boolean))];
                setTopics(uniqueTopics.sort());
            }
        } catch (error) {
            console.error('Failed to fetch questions:', error);
            alert('Failed to load questions');
        } finally {
            setLoading(false);
        }
    }, [token, searchQuery, selectedCategory, selectedDifficulty, selectedTopic]);

    useEffect(() => {
        fetchQuestions();
    }, [fetchQuestions]);

    // Debounced search
    useEffect(() => {
        const timer = setTimeout(() => {
            fetchQuestions();
        }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery]);

    const clearFilters = () => {
        setSearchQuery('');
        setSelectedCategory('');
        setSelectedDifficulty('');
        setSelectedTopic('');
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
            // Show backend error in the Errors section
            if (error.response && error.response.data && error.response.data.detail) {
                setUploadResult({
                    total: 0,
                    added: 0,
                    duplicates: 0,
                    errors: [error.response.data.detail]
                });
            } else {
                alert('Upload failed');
            }
        } finally {
            setUploading(false);
        }
    };

    const handleBulkTextUpload = async (e) => {
        e.preventDefault();
        if (!bulkText.trim()) {
            alert('Please enter questions in JSON format');
            return;
        }

        setTextUploading(true);
        setUploadResult(null);

        try {
            // Parse the JSON text
            const questionsData = JSON.parse(bulkText);

            // Create a Blob and send it as if it were a file
            const blob = new Blob([JSON.stringify(questionsData, null, 2)], { type: 'application/json' });
            const formData = new FormData();
            formData.append('file', blob, 'bulk_questions.json');

            const response = await axios.post(`${API_URL}/admin/questions/upload`, formData, {
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });
            setUploadResult(response.data);
            setBulkText('');
            fetchQuestions();
        } catch (jsonError) {
            if (jsonError instanceof SyntaxError) {
                setUploadResult({
                    total: 0,
                    added: 0,
                    duplicates: 0,
                    errors: ['Invalid JSON format. Please check your syntax.']
                });
            } else {
                console.error('Upload failed:', jsonError);
                if (jsonError.response && jsonError.response.data && jsonError.response.data.detail) {
                    setUploadResult({
                        total: 0,
                        added: 0,
                        duplicates: 0,
                        errors: [jsonError.response.data.detail]
                    });
                } else {
                    alert('Upload failed');
                }
            }
        } finally {
            setTextUploading(false);
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

                    {/* Upload Tabs */}
                    <div className="flex space-x-1 mb-4">
                        <button
                            onClick={() => setActiveUploadTab('file')}
                            className={`px-4 py-2 rounded-lg text-sm font-medium ${activeUploadTab === 'file'
                                ? 'bg-black text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                        >
                            File Upload
                        </button>
                        <button
                            onClick={() => setActiveUploadTab('text')}
                            className={`px-4 py-2 rounded-lg text-sm font-medium ${activeUploadTab === 'text'
                                ? 'bg-black text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                        >
                            Paste Questions
                        </button>
                    </div>

                    {/* Format Example */}
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                        <div className="text-sm font-medium text-gray-700 mb-2">JSON Format Example:</div>
                        <pre className="text-xs text-gray-600 overflow-x-auto">
                            {`[
  {
    "question": "If a train runs at 60 km/h for 2 hours, how far does it travel?",
    "options": ["100 km", "120 km", "110 km", "130 km"],
    "answer": "B",
    "difficulty": "Easy",
    "category": "Quantitative",
    "topic": "Speed and Distance",
    "solution": "Distance = Speed × Time = 60 × 2 = 120 km"
  }
]`}
                        </pre>
                        <div className="mt-2 text-xs text-gray-600">
                            <strong>Required fields:</strong> question, options (array), answer (A/B/C/D), difficulty (Easy/Medium/Hard), category, topic, solution
                        </div>
                    </div>

                    {/* File Upload Tab */}
                    {activeUploadTab === 'file' && (
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
                      file:bg-gray-100 file:text-gray-700
                      hover:file:bg-gray-200"
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={uploading || !uploadFile}
                                className="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {uploading ? 'Uploading...' : 'Upload Questions'}
                            </button>
                        </form>
                    )}

                    {/* Text Upload Tab */}
                    {activeUploadTab === 'text' && (
                        <form onSubmit={handleBulkTextUpload} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Paste Questions (JSON Format)
                                </label>
                                <textarea
                                    value={bulkText}
                                    onChange={(e) => setBulkText(e.target.value)}
                                    placeholder='Paste your questions in JSON format here...&#10;&#10;Example:&#10;[&#10;  {&#10;    "question": "What is 2 + 2?",&#10;    "options": ["3", "4", "5", "6"],&#10;    "answer": "B",&#10;    "difficulty": "Easy",&#10;    "topic": "Mathematics",&#10;    "solution": "Basic addition: 2 + 2 = 4"&#10;  }&#10;]'
                                    className="w-full h-64 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black resize-none font-mono text-sm"
                                />
                                <div className="mt-2 text-xs text-gray-500">
                                    💡 Tip: You can paste multiple questions in an array format. The system will automatically check for duplicates using vector similarity.
                                </div>
                            </div>
                            <button
                                type="submit"
                                disabled={textUploading || !bulkText.trim()}
                                className="px-6 py-2 bg-black text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {textUploading ? 'Processing...' : 'Upload Questions'}
                            </button>
                        </form>
                    )}

                    {/* Upload Result */}
                    {uploadResult && (
                        <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                            <div className="font-semibold text-gray-900 mb-2">Upload Results:</div>
                            <div className="text-sm text-gray-700 space-y-1">
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
                        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                            <h2 className="text-lg font-semibold text-gray-900">
                                All Questions
                                <span className="text-sm font-normal text-gray-500 ml-2">
                                    ({total} {total === 1 ? 'result' : 'results'})
                                </span>
                            </h2>

                            {/* Clear Filters Button */}
                            {(searchQuery || selectedCategory || selectedDifficulty || selectedTopic) && (
                                <button
                                    onClick={clearFilters}
                                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                                >
                                    Clear all filters
                                </button>
                            )}
                        </div>

                        {/* Search and Filters */}
                        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {/* Search Input */}
                            <div className="relative">
                                <input
                                    type="text"
                                    placeholder="Search questions..."
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                                />
                                <svg
                                    className="absolute left-3 top-2.5 h-5 w-5 text-gray-400"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                            </div>

                            {/* Category Filter */}
                            <select
                                value={selectedCategory}
                                onChange={(e) => setSelectedCategory(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                            >
                                <option value="">All Categories</option>
                                <option value="Quantitative">Quantitative</option>
                                <option value="Logical">Logical</option>
                                <option value="Linguistic">Linguistic</option>
                            </select>

                            {/* Difficulty Filter */}
                            <select
                                value={selectedDifficulty}
                                onChange={(e) => setSelectedDifficulty(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                            >
                                <option value="">All Difficulties</option>
                                <option value="Easy">Easy</option>
                                <option value="Medium">Medium</option>
                                <option value="Hard">Hard</option>
                            </select>

                            {/* Topic Filter */}
                            <select
                                value={selectedTopic}
                                onChange={(e) => setSelectedTopic(e.target.value)}
                                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                            >
                                <option value="">All Topics</option>
                                {topics.map((topic) => (
                                    <option key={topic} value={topic}>{topic}</option>
                                ))}
                            </select>
                        </div>
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
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Topic</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Difficulty</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    {questions.length === 0 ? (
                                        <tr>
                                            <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                                                {searchQuery || selectedCategory || selectedDifficulty || selectedTopic
                                                    ? 'No questions match your filters'
                                                    : 'No questions found'}
                                            </td>
                                        </tr>
                                    ) : (
                                        questions.map((question) => (
                                            <tr key={question.id} className="hover:bg-gray-50">
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    #{question.id}
                                                </td>
                                                <td className="px-6 py-4 text-sm text-gray-900">
                                                    <div className="max-w-md truncate">{question.title}</div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${question.category === 'Quantitative' ? 'bg-blue-100 text-blue-800' :
                                                        question.category === 'Logical' ? 'bg-blue-200 text-blue-900' :
                                                            question.category === 'Linguistic' ? 'bg-sky-100 text-sky-800' :
                                                                'bg-slate-100 text-slate-800'
                                                        }`}>
                                                        {question.category || 'N/A'}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                                    <div>{question.topic}</div>
                                                    {question.sub_topic && (
                                                        <div className="text-xs text-gray-400">{question.sub_topic}</div>
                                                    )}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${question.difficulty === 'easy' || question.difficulty === 'Easy' ? 'bg-sky-100 text-sky-700' :
                                                        question.difficulty === 'medium' || question.difficulty === 'Medium' ? 'bg-blue-100 text-blue-700' :
                                                            'bg-blue-600 text-white'
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
                                                        className="text-blue-600 hover:text-blue-800"
                                                    >
                                                        Delete
                                                    </button>
                                                </td>
                                            </tr>
                                        ))
                                    )}
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
