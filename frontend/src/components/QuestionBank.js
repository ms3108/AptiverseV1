import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import API_URL from '../config/api';
import axios from 'axios';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Navigation from './Navigation';

const CATEGORY_CACHE_KEY = 'aptiverse.question.categories';
const CATEGORY_CACHE_TTL = 10 * 60 * 1000; // 10 minutes

function QuestionBank() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [categories, setCategories] = useState([]);
    const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || null);
    const [selectedTopic, setSelectedTopic] = useState(searchParams.get('topic') || null);
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        difficulty: searchParams.get('difficulty') || '',
        sortBy: searchParams.get('sortBy') || 'created_at',
        sortOrder: searchParams.get('sortOrder') || 'desc'
    });
    const [questionsLoading, setQuestionsLoading] = useState(false);
    const questionCacheRef = useRef(new Map());
    const navigate = useNavigate();

    useEffect(() => {
        let isActive = true;
        const controller = new AbortController();

        const loadCategories = async () => {
            const cached = sessionStorage.getItem(CATEGORY_CACHE_KEY);
            if (cached) {
                try {
                    const parsed = JSON.parse(cached);
                    if (Date.now() - parsed.timestamp < CATEGORY_CACHE_TTL) {
                        if (isActive) {
                            setCategories(parsed.data);
                            setLoading(false);
                        }
                        return;
                    }
                } catch (error) {
                    console.error('Failed to parse cached categories', error);
                }
            }

            try {
                const categoryData = await fetchCategories(controller.signal);
                if (isActive) {
                    setCategories(categoryData);
                    setLoading(false);
                    sessionStorage.setItem(
                        CATEGORY_CACHE_KEY,
                        JSON.stringify({ data: categoryData, timestamp: Date.now() })
                    );
                }
            } catch (error) {
                if (isActive) {
                    setLoading(false);
                }
                if (!axios.isCancel(error)) {
                    console.error('Failed to load categories', error);
                }
            }
        };

        loadCategories();

        return () => {
            isActive = false;
            controller.abort();
        };
    }, []);

    const fetchQuestions = useCallback(async (signal) => {
        if (!selectedCategory && !selectedTopic) {
            setQuestions([]);
            setQuestionsLoading(false);
            return;
        }

        const params = new URLSearchParams();
        if (selectedCategory) params.append('category', selectedCategory);
        if (selectedTopic) params.append('topic', selectedTopic);
        if (filters.difficulty) params.append('difficulty', filters.difficulty);
        params.append('sort_by', filters.sortBy);
        params.append('sort_order', filters.sortOrder);

        const cacheKey = params.toString();
        const cached = questionCacheRef.current.get(cacheKey);

        // If we have cached data, return it immediately
        if (cached) {
            // Defer state updates to next tick to ensure proper batching
            setTimeout(() => {
                setQuestions(cached);
                setQuestionsLoading(false);
            }, 0);
            return;
        }

        // No cache - fetch from API
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(
                `${API_URL}/question-bank/questions?${cacheKey}`,
                {
                    headers: { Authorization: `Bearer ${token}` },
                    signal
                }
            );
            if (questionCacheRef.current.size > 20) {
                const oldestKey = questionCacheRef.current.keys().next().value;
                questionCacheRef.current.delete(oldestKey);
            }
            questionCacheRef.current.set(cacheKey, response.data.questions);
            setQuestions(response.data.questions);
            setQuestionsLoading(false);
        } catch (err) {
            if (!axios.isCancel(err)) {
                console.error('Failed to load questions', err);
            }
            setQuestionsLoading(false);
        }
    }, [selectedCategory, selectedTopic, filters]);

    useEffect(() => {
        // Update URL params when state changes
        const params = new URLSearchParams();
        if (selectedCategory) params.set('category', selectedCategory);
        if (selectedTopic) params.set('topic', selectedTopic);
        if (filters.difficulty) params.set('difficulty', filters.difficulty);
        params.set('sortBy', filters.sortBy);
        params.set('sortOrder', filters.sortOrder);

        setSearchParams(params);

        if (selectedCategory || selectedTopic) {
            // Clear previous questions immediately when topic/category changes
            setQuestions([]);
            setQuestionsLoading(true);

            const controller = new AbortController();
            fetchQuestions(controller.signal);
            return () => controller.abort();
        }

        // When backing out to categories we can clear questions and loading state
        questionCacheRef.current.clear();
        setQuestions([]);
        setQuestionsLoading(false);
        return undefined;
    }, [selectedCategory, selectedTopic, filters, fetchQuestions, setSearchParams]);

    const fetchCategories = async (signal) => {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_URL}/question-bank/categories`, {
            headers: { Authorization: `Bearer ${token}` },
            signal
        });
        return response.data.categories || [];
    };

    const handleCategoryClick = (categoryName) => {
        questionCacheRef.current.clear();
        setSelectedCategory(categoryName);
        setSelectedTopic(null);
    };

    const handleTopicClick = (topicName) => {
        setSelectedTopic(topicName);
    };

    const handleQuestionClick = (questionId) => {
        // Pass the current category and topic in state so we can return to the same view
        navigate(`/question/${questionId}`, {
            state: {
                from: 'question-bank',
                category: selectedCategory,
                topic: selectedTopic,
                filters: filters
            }
        });
    };

    const handleBackToCategories = () => {
        questionCacheRef.current.clear();
        setSelectedCategory(null);
        setSelectedTopic(null);
        setQuestions([]);
    };

    const handleBackToTopics = () => {
        questionCacheRef.current.clear();
        setSelectedTopic(null);
        setQuestions([]);
    };

    const difficultyColorMap = useMemo(() => ({
        Easy: 'text-green-600 bg-green-100',
        Medium: 'text-yellow-600 bg-yellow-100',
        Hard: 'text-red-600 bg-red-100'
    }), []);

    const getDifficultyColorClass = (difficulty) => difficultyColorMap[difficulty] || 'text-gray-600 bg-gray-100';

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    // Category Selection View
    if (!selectedCategory) {
        return (
            <>
                <Navigation />
                <div className="max-w-7xl mx-auto mt-8 px-4">
                    <div className="mb-6">
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="text-blue-600 hover:text-blue-800 flex items-center"
                        >
                            ← Back to Dashboard
                        </button>
                    </div>

                    <h1 className="text-3xl font-bold text-gray-800 mb-6">📚 Question Bank</h1>
                    <p className="text-gray-600 mb-8">Select a category to explore questions</p>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {categories.map((category) => (
                            <div
                                key={category.name}
                                onClick={() => handleCategoryClick(category.name)}
                                className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow border-2 border-transparent hover:border-blue-500"
                            >
                                <div className="text-center">
                                    <div className="text-5xl mb-4">
                                        {category.name === 'Quants' && '🔢'}
                                        {category.name === 'Logical' && '🧩'}
                                        {category.name === 'Language' && '📝'}
                                    </div>
                                    <h3 className="text-2xl font-bold text-gray-800 mb-2">
                                        {category.name}
                                    </h3>
                                    <p className="text-gray-600 mb-4">
                                        {category.total_questions} questions
                                    </p>
                                    <div className="text-sm text-gray-500">
                                        {category.topics.length} topics
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </>
        );
    }

    // Topic Selection View
    if (selectedCategory && !selectedTopic) {
        const category = categories.find(c => c.name === selectedCategory);
        return (
            <>
                <Navigation />
                <div className="max-w-7xl mx-auto mt-8 px-4">
                    <div className="mb-6">
                        <button
                            onClick={handleBackToCategories}
                            className="text-blue-600 hover:text-blue-800 flex items-center"
                        >
                            ← Back to Categories
                        </button>
                    </div>

                    <h1 className="text-3xl font-bold text-gray-800 mb-2">
                        {selectedCategory === 'Quants' && '🔢'}
                        {selectedCategory === 'Logical' && '🧩'}
                        {selectedCategory === 'Language' && '📝'}
                        {selectedCategory}
                    </h1>
                    <p className="text-gray-600 mb-8">Select a topic to view questions</p>

                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
                        {category.topics.map((topic) => (
                            <div
                                key={topic.name}
                                onClick={() => handleTopicClick(topic.name)}
                                className="bg-white rounded-lg shadow p-4 cursor-pointer hover:shadow-md transition-shadow border border-gray-200 hover:border-blue-500"
                            >
                                <h4 className="font-semibold text-gray-800 mb-2">{topic.name}</h4>
                                <p className="text-sm text-gray-600">{topic.count} questions</p>
                            </div>
                        ))}
                    </div>
                </div>
            </>
        );
    }

    // Questions List View
    return (
        <>
            <Navigation />
            <div className="max-w-7xl mx-auto mt-8 px-4">
                <div className="mb-6">
                    <button
                        onClick={handleBackToTopics}
                        className="text-blue-600 hover:text-blue-800 flex items-center"
                    >
                        ← Back to Topics
                    </button>
                </div>

                <div className="flex items-center justify-between mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-800">{selectedTopic}</h1>
                        <p className="text-gray-600">
                            {questionsLoading ? (
                                <span className="animate-pulse">Loading questions...</span>
                            ) : (
                                `${questions.length} question${questions.length !== 1 ? 's' : ''}`
                            )}
                        </p>
                    </div>
                </div>

                {/* Filters and Sorting */}
                <div className="bg-white rounded-lg shadow p-4 mb-6">
                    <div className="flex flex-wrap gap-4 items-center">
                        <div>
                            <label className="text-sm font-medium text-gray-700 mr-2">Difficulty:</label>
                            <select
                                value={filters.difficulty}
                                onChange={(e) => setFilters({ ...filters, difficulty: e.target.value })}
                                className="border border-gray-300 rounded px-3 py-1"
                            >
                                <option value="">All</option>
                                <option value="Easy">Easy</option>
                                <option value="Medium">Medium</option>
                                <option value="Hard">Hard</option>
                            </select>
                        </div>

                        <div>
                            <label className="text-sm font-medium text-gray-700 mr-2">Sort by:</label>
                            <select
                                value={filters.sortBy}
                                onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
                                className="border border-gray-300 rounded px-3 py-1"
                            >
                                <option value="created_at">Date Added</option>
                                <option value="difficulty">Difficulty</option>
                                <option value="title">Title</option>
                            </select>
                        </div>

                        <div>
                            <label className="text-sm font-medium text-gray-700 mr-2">Order:</label>
                            <select
                                value={filters.sortOrder}
                                onChange={(e) => setFilters({ ...filters, sortOrder: e.target.value })}
                                className="border border-gray-300 rounded px-3 py-1"
                            >
                                <option value="desc">Descending</option>
                                <option value="asc">Ascending</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* Questions List */}
                {questionsLoading && (
                    <>
                        <div className="flex items-center justify-center mb-6">
                            <div className="text-center">
                                <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-3" style={{ borderColor: '#1E88E5' }}></div>
                                <p className="text-gray-600 font-medium">Loading questions...</p>
                            </div>
                        </div>
                        <div className="space-y-4 mb-6" aria-live="polite" aria-busy="true">
                            {[...Array(3)].map((_, idx) => (
                                <div
                                    key={`question-skeleton-${idx}`}
                                    className="bg-white rounded-lg shadow p-6 animate-pulse"
                                >
                                    <div className="flex items-start gap-3 mb-3">
                                        <div className="w-6 h-6 bg-gray-200 rounded-full"></div>
                                        <div className="h-5 bg-gray-200 rounded w-1/3"></div>
                                    </div>
                                    <div className="h-4 bg-gray-200 rounded w-2/3 mb-2"></div>
                                    <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                                    <div className="flex gap-2">
                                        <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                                        <div className="h-6 bg-gray-200 rounded-full w-16"></div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </>
                )}

                {!questionsLoading && (
                    <div className="space-y-4">
                        {questions.map((question) => (
                            <div
                                key={question.id}
                                onClick={() => handleQuestionClick(question.id)}
                                className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3 mb-2">
                                            {question.solved ? (
                                                <span className="text-green-600 text-xl font-bold" title="Solved correctly">
                                                    ✓
                                                </span>
                                            ) : question.attempted ? (
                                                <span className="text-orange-500 text-xl font-bold" title="Attempted but not solved">
                                                    ◐
                                                </span>
                                            ) : (
                                                <span className="text-gray-300 text-xl font-bold" title="Not attempted">
                                                    ○
                                                </span>
                                            )}
                                            <h3 className="text-xl font-semibold text-gray-800">
                                                {question.title}
                                            </h3>
                                        </div>
                                        <p className="text-gray-600 mb-3">{question.description}</p>
                                        <div className="flex items-center gap-3">
                                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDifficultyColorClass(question.difficulty)}`}>
                                                {question.difficulty}
                                            </span>
                                            <span className="text-sm text-gray-500">
                                                💎 {question.xp_reward} XP
                                            </span>
                                            {question.solved && (
                                                <span className="text-xs text-green-600 font-medium">
                                                    Solved
                                                </span>
                                            )}
                                            {!question.solved && question.attempted && (
                                                <span className="text-xs text-orange-500 font-medium">
                                                    Attempted
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="text-blue-600 text-2xl">→</div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {!questionsLoading && questions.length === 0 && (
                    <div className="bg-white rounded-lg shadow-sm p-12 text-center">
                        <div className="text-6xl mb-4">🔍</div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">No Questions Found</h3>
                        <p className="text-gray-600">
                            No questions match your current filters. Try adjusting the difficulty or sort options.
                        </p>
                    </div>
                )}
            </div>
        </>
    );
}

export default QuestionBank;


