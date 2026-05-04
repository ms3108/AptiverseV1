
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
    const [activeUploadTab, setActiveUploadTab] = useState('file'); // 'file', 'text', or 'generate'

    // Question generation state
    const [genTopic, setGenTopic] = useState('');
    const [genDifficulty, setGenDifficulty] = useState('Easy');
    const [genCount, setGenCount] = useState(1);
    const [generating, setGenerating] = useState(false);
    const [generateResult, setGenerateResult] = useState(null);
    const [showGenModal, setShowGenModal] = useState(false);
    const [modalQuestions, setModalQuestions] = useState([]);

    // Search and filter state
    const [searchQuery, setSearchQuery] = useState('');
    const [selectedCategory, setSelectedCategory] = useState('');
    const [selectedDifficulty, setSelectedDifficulty] = useState('');
    const [selectedTopic, setSelectedTopic] = useState('');
    const [topics, setTopics] = useState([]);

    // Pagination state
    const [currentPage, setCurrentPage] = useState(1);
    const questionsPerPage = 50;

    // Calculate pagination
    const indexOfLastQuestion = currentPage * questionsPerPage;
    const indexOfFirstQuestion = indexOfLastQuestion - questionsPerPage;
    const currentQuestions = questions.slice(indexOfFirstQuestion, indexOfLastQuestion);
    const totalPages = Math.ceil(questions.length / questionsPerPage);

    const fetchQuestions = useCallback(async () => {
        setLoading(true);
        try {
            const params = { limit: 1000 };
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
        } catch (error) {
            console.error('Failed to fetch questions:', error);
            alert('Failed to load questions');
        } finally {
            setLoading(false);
        }
    }, [token, searchQuery, selectedCategory, selectedDifficulty, selectedTopic]);

    const fetchTopics = useCallback(async () => {
        try {
            const response = await axios.get(`${API_URL}/admin/topics`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setTopics(response.data);
        } catch (error) {
            console.error('Failed to fetch topics:', error);
        }
    }, [token]);

    useEffect(() => {
        fetchQuestions();
        fetchTopics();
    }, [fetchQuestions, fetchTopics]);

    // Debounced search
    useEffect(() => {
        const timer = setTimeout(() => {
            setCurrentPage(1); // Reset to first page when searching
            fetchQuestions();
        }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery]);

    // Reset pagination when filters change
    useEffect(() => {
        setCurrentPage(1);
    }, [selectedCategory, selectedDifficulty, selectedTopic]);

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
                    stats: {
                        total_in_file: 0,
                        added: 0,
                        errors_count: 1
                    },
                    errors: [error.response.data.detail]
                });
            } else {
                alert('Upload failed');
            }
        } finally {
            setUploading(false);
        }
    };

    const handleGenerateQuestions = async (e) => {
        e.preventDefault();
        if (!genTopic.trim()) {
            alert('Please enter a topic');
            return;
        }

        setGenerating(true);
        setGenerateResult(null);

        try {
            const response = await axios.post(
                `${API_URL}/admin/questions/generate`,
                null,
                {
                    params: {
                        topic: genTopic,
                        difficulty: genDifficulty,
                        count: genCount
                    },
                    headers: { Authorization: `Bearer ${token}` }
                }
            );

            setGenerateResult(response.data);
            setGenTopic('');
            fetchQuestions();
            // Open modal if questions were added
            if (response.data.questions && response.data.questions.length > 0) {
                setModalQuestions(response.data.questions);
                setShowGenModal(true);
            }
        } catch (error) {
            console.error('Generation failed:', error);
            if (error.response && error.response.data && error.response.data.detail) {
                setGenerateResult({
                    error: error.response.data.detail
                });
            } else {
                setGenerateResult({
                    error: 'Failed to generate questions'
                });
            }
        } finally {
            setGenerating(false);
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
                    stats: {
                        total_in_file: 0,
                        added: 0,
                        errors_count: 1
                    },
                    errors: ['Invalid JSON format. Please check your syntax.']
                });
            } else {
                console.error('Upload failed:', jsonError);
                if (jsonError.response && jsonError.response.data && jsonError.response.data.detail) {
                    setUploadResult({
                        stats: {
                            total_in_file: 0,
                            added: 0,
                            errors_count: 1
                        },
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

    const handleDeleteAllQuestions = async () => {
        if (!window.confirm(`Are you sure you want to delete ALL ${total} questions? This action cannot be undone!`)) {
            return;
        }

        // Double confirmation for safety
        const confirmation = prompt(`To confirm deletion of ALL questions, please type "DELETE ALL" exactly:`);
        if (confirmation !== "DELETE ALL") {
            alert('Deletion cancelled - confirmation text did not match');
            return;
        }

        try {
            const response = await axios.delete(`${API_URL}/admin/questions/delete-all`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            alert(`Successfully deleted ${response.data.deleted_count} questions`);
            fetchQuestions(); // Refresh the list
        } catch (error) {
            console.error('Delete all failed:', error);
            const errorMessage = error.response?.data?.detail
                || error.response?.data?.message
                || error.message
                || 'Unknown error occurred';
            alert(`Failed to delete questions: ${errorMessage}`);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50">
            <Navigation />

            {/* Generated Questions Modal */}
            {showGenModal && modalQuestions.length > 0 && (
                <GeneratedQuestionsModal
                    questions={modalQuestions}
                    onClose={() => setShowGenModal(false)}
                />
            )}

            <div className="max-w-7xl mx-auto px-4 py-8">
                {/* Header */}
                <div className="mb-6">
                    <div className="flex justify-between items-center">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Question Management</h1>
                            <p className="text-gray-600 mt-2">Total Questions: {total}</p>
                        </div>
                        <button
                            onClick={handleDeleteAllQuestions}
                            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium shadow-lg"
                            title={`Delete all ${total} questions`}
                        >
                            🗑️ Delete All Questions ({total})
                        </button>
                    </div>
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
                            📁 File Upload
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
                        <button
                            onClick={() => setActiveUploadTab('generate')}
                            className={`px-4 py-2 rounded-lg text-sm font-medium ${activeUploadTab === 'generate'
                                ? 'bg-purple-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                                }`}
                        >
                            ✨ Generate with AI
                        </button>
                    </div>

                    {/* Format Example - Upload Methods */}
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
                        <div className="text-sm font-medium text-gray-700 mb-2">JSON Format Example:</div>
                        <pre className="text-xs text-gray-600 overflow-x-auto">
                            {`[
  {
    "title": "Train Speed Distance Problem",
    "description": "If a train runs at 60 km/h for 2 hours, how far does it travel?",
    "difficulty": "Easy",
    "category": "Quantitative",
    "topic": "Speed and Distance",
    "option_a": "100 km",
    "option_b": "120 km",
    "option_c": "110 km",
    "option_d": "130 km",
    "correct_answer": "B",
    "explanation": "Distance = Speed × Time = 60 × 2 = 120 km",
    "xp_reward": 10
  }
]`}
                        </pre>
                        <div className="mt-2 text-xs text-gray-600">
                            <strong>Required fields:</strong> title, description, difficulty (Easy/Medium/Hard), category, topic, option_a, option_b, option_c, option_d, correct_answer (A/B/C/D), explanation, xp_reward
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

                    {/* Generate with AI Tab */}
                    {activeUploadTab === 'generate' && (
                        <form onSubmit={handleGenerateQuestions} className="space-y-4">
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                                <p className="text-sm text-blue-800">
                                    ✨ Generate questions using <strong>AI</strong>. Specify a topic and difficulty level, and the questions will be saved directly to the database.
                                </p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Topic *
                                    </label>
                                    <input
                                        type="text"
                                        list="gen-topic-list"
                                        value={genTopic}
                                        onChange={(e) => setGenTopic(e.target.value)}
                                        placeholder="e.g., Profit and Loss, Time and Work"
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black"
                                        disabled={generating}
                                    />
                                    <datalist id="gen-topic-list">
                                        {topics.map(t => (
                                            <option key={t} value={t} />
                                        ))}
                                    </datalist>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Difficulty
                                    </label>
                                    <select
                                        value={genDifficulty}
                                        onChange={(e) => setGenDifficulty(e.target.value)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black bg-white"
                                        disabled={generating}
                                    >
                                        <option value="Easy">Easy</option>
                                        <option value="Medium">Medium</option>
                                        <option value="Hard">Hard</option>
                                    </select>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Number of Questions
                                    </label>
                                    <input
                                        type="number"
                                        min="1"
                                        max="5"
                                        value={genCount}
                                        onChange={(e) => setGenCount(Math.max(1, Math.min(5, parseInt(e.target.value) || 1)))}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-black focus:border-black"
                                        disabled={generating}
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={generating || !genTopic.trim()}
                                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-all"
                            >
                                {generating ? 'Generating... 🤖' : 'Generate with AI ⚡'}
                            </button>
                        </form>
                    )}

                    {/* Upload Result */}
                    {uploadResult && (
                        <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg">
                            <div className="font-semibold text-gray-900 mb-2">Upload Results:</div>
                            <div className="text-sm text-gray-700 space-y-1">
                                <div>✅ Total processed: {uploadResult.stats?.total_in_file || uploadResult.total || 0}</div>
                                <div>✅ Successfully added: {uploadResult.stats?.added || uploadResult.added || 0}</div>
                                {(uploadResult.stats?.errors_count > 0 || uploadResult.duplicates > 0) && (
                                    <div>⚠️ Issues: {uploadResult.stats?.errors_count || uploadResult.duplicates || 0}</div>
                                )}
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

                    {/* Generate Result */}
                    {generateResult && (
                        <div className={`mt-4 p-4 rounded-lg border ${generateResult.error ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                            {generateResult.error ? (
                                <div className="text-red-800">
                                    <div className="font-semibold">Error:</div>
                                    <div className="text-sm mt-1">{generateResult.error}</div>
                                </div>
                            ) : (
                                <div className="text-green-800">
                                    <div className="font-semibold mb-3">Generation Results:</div>
                                    <div className="grid grid-cols-2 gap-4 mb-4">
                                        <div>
                                            <div className="text-sm opacity-75">Generated</div>
                                            <div className="text-2xl font-bold">{generateResult.generated || 0}</div>
                                        </div>
                                        <div>
                                            <div className="text-sm opacity-75">Added to DB</div>
                                            <div className="text-2xl font-bold">{generateResult.added || 0}</div>
                                        </div>
                                    </div>

                                    {generateResult.duplicate_summary && generateResult.duplicate_summary.length > 0 && (
                                        <div className="mt-4 pt-4 border-t border-green-300">
                                            <div className="font-medium text-sm mb-2">⚠️ Duplicates Found:</div>
                                            <div className="text-xs space-y-1">
                                                {generateResult.duplicate_summary.map((dup, idx) => (
                                                    <div key={idx} className="flex justify-between items-center bg-white/50 p-2 rounded">
                                                        <span>{dup.title}</span>
                                                        <span className="text-gray-600">{(dup.similarity * 100).toFixed(0)}% match</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    {generateResult.questions && generateResult.questions.length > 0 && (
                                        <div className="mt-4 pt-4 border-t border-green-300">
                                            <div className="font-medium text-sm mb-2">✨ New Questions Created:</div>
                                            <div className="text-xs space-y-2 max-h-48 overflow-y-auto">
                                                {generateResult.questions.map((q, idx) => (
                                                    <div key={idx} className="bg-white/50 p-2 rounded">
                                                        <div className="font-medium">{q.title}</div>
                                                        <div className="text-gray-700">{q.difficulty} • {q.topic}</div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
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
                                    {totalPages > 1 && (
                                        <> • Page {currentPage} of {totalPages}</>
                                    )}
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
                                <option value="Quants">Quants</option>
                                <option value="Logical">Logical</option>
                                <option value="Linguistics">Linguistics</option>
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
                                    {currentQuestions.length === 0 ? (
                                        <tr>
                                            <td colSpan={8} className="px-6 py-8 text-center text-gray-500">
                                                {searchQuery || selectedCategory || selectedDifficulty || selectedTopic
                                                    ? 'No questions match your filters'
                                                    : 'No questions found'}
                                            </td>
                                        </tr>
                                    ) : (
                                        currentQuestions.map((question) => (
                                            <tr key={question.id} className="hover:bg-gray-50">
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    #{question.id}
                                                </td>
                                                <td className="px-6 py-4 text-sm text-gray-900">
                                                    <div className="max-w-md truncate">{question.title}</div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${question.category === 'Quants' ? 'bg-blue-100 text-blue-800' :
                                                        question.category === 'Logical' ? 'bg-blue-200 text-blue-900' :
                                                            question.category === 'Linguistics' ? 'bg-sky-100 text-sky-800' :
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

                {/* Pagination Controls */}
                {totalPages > 1 && (
                    <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
                        <div className="flex items-center justify-between">
                            <div className="flex-1 flex justify-between sm:hidden">
                                <button
                                    onClick={() => setCurrentPage(Math.max(currentPage - 1, 1))}
                                    disabled={currentPage === 1}
                                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Previous
                                </button>
                                <button
                                    onClick={() => setCurrentPage(Math.min(currentPage + 1, totalPages))}
                                    disabled={currentPage === totalPages}
                                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    Next
                                </button>
                            </div>
                            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                                <div>
                                    <p className="text-sm text-gray-700">
                                        Showing{' '}
                                        <span className="font-medium">{indexOfFirstQuestion + 1}</span>
                                        {' '}to{' '}
                                        <span className="font-medium">
                                            {Math.min(indexOfLastQuestion, questions.length)}
                                        </span>
                                        {' '}of{' '}
                                        <span className="font-medium">{questions.length}</span>
                                        {' '}results
                                    </p>
                                </div>
                                <div>
                                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                                        <button
                                            onClick={() => setCurrentPage(Math.max(currentPage - 1, 1))}
                                            disabled={currentPage === 1}
                                            className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            <span className="sr-only">Previous</span>
                                            <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                                            </svg>
                                        </button>

                                        {/* Page Numbers */}
                                        {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                                            let pageNumber;
                                            if (totalPages <= 7) {
                                                pageNumber = i + 1;
                                            } else if (currentPage <= 4) {
                                                pageNumber = i + 1;
                                            } else if (currentPage >= totalPages - 3) {
                                                pageNumber = totalPages - 6 + i;
                                            } else {
                                                pageNumber = currentPage - 3 + i;
                                            }

                                            return (
                                                <button
                                                    key={pageNumber}
                                                    onClick={() => setCurrentPage(pageNumber)}
                                                    className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${currentPage === pageNumber
                                                        ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                                                        }`}
                                                >
                                                    {pageNumber}
                                                </button>
                                            );
                                        })}

                                        <button
                                            onClick={() => setCurrentPage(Math.min(currentPage + 1, totalPages))}
                                            disabled={currentPage === totalPages}
                                            className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                                        >
                                            <span className="sr-only">Next</span>
                                            <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                                            </svg>
                                        </button>
                                    </nav>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

/* ─────────────────────────────────────────────────────────────────────────────
   Generated Questions Modal
───────────────────────────────────────────────────────────────────────────── */
const OPTION_LABELS = ['A', 'B', 'C', 'D'];
const OPTION_KEYS   = ['option_a', 'option_b', 'option_c', 'option_d'];

const DIFFICULTY_STYLES = {
    easy:   { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
    medium: { bg: 'bg-amber-100',   text: 'text-amber-700',   dot: 'bg-amber-500'   },
    hard:   { bg: 'bg-rose-100',    text: 'text-rose-700',    dot: 'bg-rose-500'    },
};

const GeneratedQuestionsModal = ({ questions, onClose }) => {
    const [activeIdx, setActiveIdx] = useState(0);
    const [revealed, setRevealed] = useState(false);
    const total = questions.length;
    const q = questions[activeIdx];

    // Keyboard navigation
    React.useEffect(() => {
        const handler = (e) => {
            if (e.key === 'Escape') onClose();
            if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
                setActiveIdx(i => Math.min(i + 1, total - 1));
                setRevealed(false);
            }
            if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                setActiveIdx(i => Math.max(i - 1, 0));
                setRevealed(false);
            }
        };
        window.addEventListener('keydown', handler);
        return () => window.removeEventListener('keydown', handler);
    }, [onClose, total]);

    const goTo = (idx) => { setActiveIdx(idx); setRevealed(false); };

    const diffKey  = (q.difficulty || 'easy').toLowerCase();
    const diffStyle = DIFFICULTY_STYLES[diffKey] || DIFFICULTY_STYLES.easy;
    const correctLetter = (q.correct_answer || 'A').toUpperCase();

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            style={{ background: 'rgba(0,0,0,0.65)', backdropFilter: 'blur(6px)' }}
            onClick={(e) => e.target === e.currentTarget && onClose()}
        >
            <div
                className="relative w-full max-w-2xl bg-white rounded-2xl shadow-2xl overflow-hidden"
                style={{ maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}
            >
                {/* ── Header ── */}
                <div className="px-6 pt-5 pb-4 border-b border-gray-100" style={{ background: 'linear-gradient(135deg,#7c3aed,#4f46e5)' }}>
                    <div className="flex items-center justify-between">
                        <div>
                            <div className="flex items-center gap-2">
                                <span className="text-white text-xl">✨</span>
                                <h2 className="text-white font-bold text-lg">Generated Questions</h2>
                            </div>
                            <p className="text-purple-200 text-sm mt-0.5">
                                {total} question{total !== 1 ? 's' : ''} saved to the database
                            </p>
                        </div>
                        <button
                            onClick={onClose}
                            className="text-white/70 hover:text-white transition-colors text-2xl leading-none"
                            aria-label="Close"
                        >
                            ×
                        </button>
                    </div>

                    {/* Progress dots */}
                    {total > 1 && (
                        <div className="flex gap-1.5 mt-3">
                            {questions.map((_, i) => (
                                <button
                                    key={i}
                                    onClick={() => goTo(i)}
                                    className={`h-2 rounded-full transition-all ${
                                        i === activeIdx
                                            ? 'bg-white w-6'
                                            : 'bg-white/40 w-2 hover:bg-white/70'
                                    }`}
                                />
                            ))}
                        </div>
                    )}
                </div>

                {/* ── Body (scrollable) ── */}
                <div className="overflow-y-auto flex-1 px-6 py-5" style={{ scrollbarWidth: 'thin' }}>
                    {/* Meta row */}
                    <div className="flex flex-wrap gap-2 mb-4">
                        <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold ${diffStyle.bg} ${diffStyle.text}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${diffStyle.dot}`} />
                            {q.difficulty}
                        </span>
                        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-indigo-100 text-indigo-700">
                            📚 {q.topic}
                        </span>
                        {q.category && (
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-sky-100 text-sky-700">
                                {q.category}
                            </span>
                        )}
                        {q.xp_reward && (
                            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-yellow-100 text-yellow-700">
                                ⚡ {q.xp_reward} XP
                            </span>
                        )}
                    </div>

                    {/* Question text */}
                    <div className="mb-5">
                        <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">
                            Question {activeIdx + 1} of {total}
                        </p>
                        <p className="text-gray-900 font-medium leading-relaxed text-base">
                            {q.description || q.title}
                        </p>
                    </div>

                    {/* Options */}
                    <div className="space-y-2.5 mb-5">
                        {OPTION_LABELS.map((letter, idx) => {
                            const optionText = q[OPTION_KEYS[idx]];
                            const isCorrect  = letter === correctLetter;
                            let optionClass = 'border border-gray-200 bg-gray-50 text-gray-700';
                            if (revealed) {
                                optionClass = isCorrect
                                    ? 'border-2 border-emerald-500 bg-emerald-50 text-emerald-800'
                                    : 'border border-gray-200 bg-gray-50 text-gray-400';
                            }
                            return (
                                <div
                                    key={letter}
                                    className={`flex items-start gap-3 p-3 rounded-xl transition-all ${optionClass}`}
                                >
                                    <span
                                        className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold ${
                                            revealed && isCorrect
                                                ? 'bg-emerald-500 text-white'
                                                : 'bg-white border border-gray-300 text-gray-600'
                                        }`}
                                    >
                                        {revealed && isCorrect ? '✓' : letter}
                                    </span>
                                    <span className="text-sm leading-relaxed pt-0.5">{optionText}</span>
                                </div>
                            );
                        })}
                    </div>

                    {/* Reveal / Explanation */}
                    {!revealed ? (
                        <button
                            onClick={() => setRevealed(true)}
                            className="w-full py-2.5 rounded-xl border-2 border-dashed border-purple-300 text-purple-600 text-sm font-semibold hover:bg-purple-50 transition-colors"
                        >
                            👁 Reveal Answer & Explanation
                        </button>
                    ) : (
                        <div className="rounded-xl p-4" style={{ background: 'linear-gradient(135deg,#f0fdf4,#dcfce7)', border: '1px solid #86efac' }}>
                            <div className="flex items-center gap-2 mb-2">
                                <span className="w-6 h-6 rounded-full bg-emerald-500 text-white flex items-center justify-center text-xs font-bold">✓</span>
                                <span className="font-bold text-emerald-800 text-sm">Correct Answer: Option {correctLetter}</span>
                            </div>
                            {q.explanation && (
                                <p className="text-emerald-900 text-sm leading-relaxed">{q.explanation}</p>
                            )}
                        </div>
                    )}
                </div>

                {/* ── Footer Nav ── */}
                <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between gap-3 bg-gray-50">
                    <button
                        onClick={() => goTo(Math.max(activeIdx - 1, 0))}
                        disabled={activeIdx === 0}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-gray-600 bg-white border border-gray-200 hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                    >
                        ← Prev
                    </button>

                    <span className="text-xs text-gray-400">
                        {activeIdx + 1} / {total}
                    </span>

                    {activeIdx < total - 1 ? (
                        <button
                            onClick={() => goTo(activeIdx + 1)}
                            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
                        >
                            Next →
                        </button>
                    ) : (
                        <button
                            onClick={onClose}
                            className="flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium text-white bg-emerald-600 hover:bg-emerald-700 transition-colors"
                        >
                            Done ✓
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AdminQuestions;
