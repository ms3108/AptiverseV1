import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import API_URL from '../config/api';
import axios from 'axios';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Navigation from './Navigation';
import AdminQuestionForm from './AdminQuestionForm';
import { useAuth } from '../context/AuthContext';

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
    const [hasLoadedQuestions, setHasLoadedQuestions] = useState(false);
    const [error, setError] = useState(null);
    const [showAddQuestionModal, setShowAddQuestionModal] = useState(false);
    const questionCacheRef = useRef(new Map());
    const navigate = useNavigate();
    const { user } = useAuth();
    const isAdmin = user?.is_admin;

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

        // If we have cached data, return it immediately WITHOUT showing loading state
        if (cached) {
            setQuestions(cached);
            setQuestionsLoading(false);
            setHasLoadedQuestions(true);
            return;
        }

        // No cache - show loading state and fetch from API
        setQuestionsLoading(true);
        setError(null);

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
            setHasLoadedQuestions(true);
        } catch (err) {
            if (!axios.isCancel(err)) {
                console.error('Failed to load questions', err);
                setError('Unable to load questions right now. Please try again.');
                setHasLoadedQuestions(true);
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
            // Reset loaded state when changing topic/category
            setHasLoadedQuestions(false);
            setQuestions([]);
            setError(null);

            const controller = new AbortController();
            fetchQuestions(controller.signal);
            return () => controller.abort();
        }

        // When backing out to categories we can clear questions and loading state
        questionCacheRef.current.clear();
        setQuestions([]);
        setQuestionsLoading(false);
        setHasLoadedQuestions(false);
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

    const handleAddQuestionClick = () => {
        setShowAddQuestionModal(true);
    };

    const handleCloseModal = () => {
        setShowAddQuestionModal(false);
    };

    const handleBackdropClick = (e) => {
        // Only close if clicking the backdrop itself, not its children
        if (e.target === e.currentTarget) {
            handleCloseModal();
        }
    };

    // Prevent body scroll when modal is open
    useEffect(() => {
        if (showAddQuestionModal) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = 'unset';
        }

        // Cleanup on unmount
        return () => {
            document.body.style.overflow = 'unset';
        };
    }, [showAddQuestionModal]);

    const handleQuestionCreated = (data) => {
        // Clear caches to force refresh
        sessionStorage.removeItem(CATEGORY_CACHE_KEY);
        questionCacheRef.current.clear();

        // Reload categories to get updated counts
        const controller = new AbortController();
        fetchCategories(controller.signal)
            .then(categoryData => {
                setCategories(categoryData);
                sessionStorage.setItem(
                    CATEGORY_CACHE_KEY,
                    JSON.stringify({ data: categoryData, timestamp: Date.now() })
                );
            })
            .catch(error => {
                if (!axios.isCancel(error)) {
                    console.error('Failed to reload categories', error);
                }
            });

        // If we're viewing questions, reload them
        if (selectedCategory || selectedTopic) {
            fetchQuestions(controller.signal);
        }
    };

    const difficultyColorMap = useMemo(() => ({
        Easy: 'text-gray-600 bg-gray-100',
        Medium: 'text-gray-700 bg-gray-200',
        Hard: 'text-black bg-gray-300'
    }), []);

    const getDifficultyColorClass = (difficulty) => difficultyColorMap[difficulty] || 'text-gray-600 bg-gray-100';

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen" style={{ background: '#FFFFFF' }}>
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-4 border-gray-200 border-t-black mx-auto mb-4"></div>
                    <p className="text-gray-600 font-medium">Loading Question Bank...</p>
                </div>
            </div>
        );
    }

    // Category card styles - unified black/white palette
    const categoryStyles = {
        'Quants': {
            gradient: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
            bgLight: '#F8F9FA',
            border: '#6C757D',
            icon: '🔢',
            iconBg: 'rgba(0, 0, 0, 0.12)'
        },
        'Logical': {
            gradient: 'linear-gradient(135deg, #333333 0%, #555555 100%)',
            bgLight: '#F8F9FA',
            border: '#6C757D',
            icon: '🧩',
            iconBg: 'rgba(51, 51, 51, 0.12)'
        },
        'Linguistics': {
            gradient: 'linear-gradient(135deg, #555555 0%, #777777 100%)',
            bgLight: '#F8F9FA',
            border: '#6C757D',
            icon: '📝',
            iconBg: 'rgba(85, 85, 85, 0.12)'
        }
    };

    const getStyle = (name) => categoryStyles[name] || {
        gradient: 'linear-gradient(135deg, #475569 0%, #64748B 100%)',
        bgLight: '#F1F5F9',
        border: '#CBD5E1',
        icon: '📚',
        iconBg: 'rgba(71, 85, 105, 0.12)'
    };

    // Category Selection View
    if (!selectedCategory) {
        return (
            <>
                <Navigation />
                <div style={{ background: 'linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 50%, #F8FAFC 100%)', minHeight: 'calc(100vh - 64px)' }}>
                    <div className="max-w-7xl mx-auto pt-10 pb-16 px-4">
                        {/* Back button */}
                        <button
                            onClick={() => navigate('/dashboard')}
                            className="group flex items-center gap-2 mb-8 text-gray-600 hover:text-blue-600 transition-colors"
                        >
                            <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-white shadow-sm group-hover:shadow group-hover:bg-blue-50 transition-all">
                                ←
                            </span>
                            <span className="font-medium">Back to Dashboard</span>
                        </button>

                        {/* Header */}
                        <div className="mb-10">
                            <h1 className="text-3xl font-bold mb-2" style={{ color: '#1F2937', letterSpacing: '-0.5px' }}>Question Bank</h1>
                            <p className="text-base" style={{ color: '#6B7280' }}>Select a category to explore questions</p>
                        </div>

                        {/* Category Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            {categories.map((category) => {
                                const style = getStyle(category.name);
                                return (
                                    <div
                                        key={category.name}
                                        onClick={() => handleCategoryClick(category.name)}
                                        className="group relative bg-white rounded-2xl cursor-pointer transition-all duration-300 overflow-hidden"
                                        style={{
                                            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                                            border: `2px solid ${style.border}`,
                                        }}
                                        onMouseEnter={(e) => {
                                            e.currentTarget.style.transform = 'translateY(-8px)';
                                            e.currentTarget.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.currentTarget.style.transform = 'translateY(0)';
                                            e.currentTarget.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.08)';
                                        }}
                                    >
                                        {/* Gradient header bar */}
                                        <div className="h-2" style={{ background: style.gradient }}></div>

                                        <div className="p-8">
                                            {/* Icon */}
                                            <div className="flex justify-center mb-6">
                                                <div className="flex items-center justify-center w-20 h-20 rounded-2xl transition-transform group-hover:scale-110" style={{ background: style.iconBg }}>
                                                    <span className="text-5xl">{style.icon}</span>
                                                </div>
                                            </div>

                                            {/* Content */}
                                            <div className="text-center">
                                                <h3 className="text-2xl font-bold mb-3" style={{ color: '#1F2937' }}>
                                                    {category.name}
                                                </h3>
                                                <p className="text-3xl font-black mb-1" style={{ color: '#1E40AF' }}>
                                                    {category.total_questions}
                                                </p>
                                                <p className="text-sm font-medium mb-4" style={{ color: '#6B7280' }}>questions available</p>

                                                {/* Topics badge */}
                                                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full" style={{ backgroundColor: style.bgLight }}>
                                                    <span className="text-sm">📁</span>
                                                    <span className="text-sm font-semibold" style={{ color: '#4B5563' }}>{category.topics.length} topics</span>
                                                </div>
                                            </div>

                                            {/* Arrow indicator */}
                                            <div className="absolute bottom-6 right-6 w-10 h-10 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all" style={{ background: style.gradient }}>
                                                <span className="text-white text-lg">→</span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </>
        );
    }

    // Topic Selection View
    if (selectedCategory && !selectedTopic) {
        const category = categories.find(c => c.name === selectedCategory);
        const style = getStyle(selectedCategory);
        return (
            <>
                <Navigation />
                <div style={{ background: 'linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 50%, #F8FAFC 100%)', minHeight: 'calc(100vh - 64px)' }}>
                    <div className="max-w-7xl mx-auto pt-10 pb-16 px-4">
                        {/* Back button */}
                        <button
                            onClick={handleBackToCategories}
                            className="group flex items-center gap-2 mb-8 text-gray-600 hover:text-blue-600 transition-colors"
                        >
                            <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-white shadow-sm group-hover:shadow group-hover:bg-blue-50 transition-all">
                                ←
                            </span>
                            <span className="font-medium">Back to Categories</span>
                        </button>

                        {/* Header */}
                        <div className="flex items-center gap-6 mb-10">
                            <div className="flex items-center justify-center w-16 h-16 rounded-2xl" style={{ background: style.iconBg }}>
                                <span className="text-4xl">{style.icon}</span>
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold" style={{ color: '#1F2937', letterSpacing: '-0.5px' }}>{selectedCategory}</h1>
                                <p className="text-gray-500 mt-1">Select a topic to start practicing</p>
                            </div>
                        </div>

                        {/* Topics Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
                            {category.topics.map((topic, index) => {
                                // Alternate colors for visual interest
                                const colors = [
                                    { bg: '#F8F9FA', border: '#E5E7EB', accent: '#000000' },
                                    { bg: '#F1F5F9', border: '#CBD5E1', accent: '#334155' },
                                    { bg: '#F9FAFB', border: '#D1D5DB', accent: '#374151' },
                                    { bg: '#F8FAFC', border: '#E2E8F0', accent: '#475569' },
                                    { bg: '#FAFAFA', border: '#E4E4E7', accent: '#52525B' },
                                    { bg: '#F4F4F5', border: '#D4D4D8', accent: '#3F3F46' },
                                ];
                                const color = colors[index % colors.length];

                                return (
                                    <div
                                        key={topic.name}
                                        onClick={() => handleTopicClick(topic.name)}
                                        className="group relative bg-white rounded-xl cursor-pointer transition-all duration-300 overflow-hidden"
                                        style={{
                                            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
                                            border: `1px solid ${color.border}`,
                                        }}
                                        onMouseEnter={(e) => {
                                            e.currentTarget.style.transform = 'translateY(-4px)';
                                            e.currentTarget.style.boxShadow = '0 12px 24px rgba(0, 0, 0, 0.12)';
                                            e.currentTarget.style.borderColor = color.accent;
                                        }}
                                        onMouseLeave={(e) => {
                                            e.currentTarget.style.transform = 'translateY(0)';
                                            e.currentTarget.style.boxShadow = '0 2px 12px rgba(0, 0, 0, 0.06)';
                                            e.currentTarget.style.borderColor = color.border;
                                        }}
                                    >
                                        {/* Colored top accent */}
                                        <div className="h-1" style={{ backgroundColor: color.accent }}></div>

                                        <div className="p-5">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <h4 className="font-bold text-gray-800 mb-2 group-hover:text-gray-900 transition-colors">{topic.name}</h4>
                                                    <div className="flex items-center gap-2">
                                                        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold" style={{ backgroundColor: color.bg, color: color.accent }}>
                                                            {topic.count} questions
                                                        </span>
                                                    </div>
                                                </div>
                                                <div className="w-8 h-8 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all" style={{ backgroundColor: color.bg }}>
                                                    <span style={{ color: color.accent }}>→</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>

                        {/* Category summary */}
                        <div className="mt-10 p-6 rounded-2xl bg-white" style={{ boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-xl flex items-center justify-center" style={{ background: style.gradient }}>
                                        <span className="text-2xl text-white">📊</span>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500">Category Statistics</p>
                                        <p className="font-bold text-gray-800">{category.total_questions} questions across {category.topics.length} topics</p>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-sm text-gray-500">Ready to practice?</p>
                                    <p className="font-semibold" style={{ color: style.gradient.includes('000000') ? '#000000' : style.gradient.includes('333333') ? '#333333' : '#555555' }}>Select a topic above</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </>
        );
    }

    // Questions List View
    const style = getStyle(selectedCategory);
    return (
        <>
            <Navigation />
            <div style={{ background: 'linear-gradient(180deg, #F8FAFC 0%, #EEF2FF 50%, #F8FAFC 100%)', minHeight: 'calc(100vh - 64px)' }}>
                <div className="max-w-7xl mx-auto pt-10 pb-16 px-4">
                    {/* Back button */}
                    <button
                        onClick={handleBackToTopics}
                        className="group flex items-center gap-2 mb-8 text-gray-600 hover:text-blue-600 transition-colors"
                    >
                        <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-white shadow-sm group-hover:shadow group-hover:bg-blue-50 transition-all">
                            ←
                        </span>
                        <span className="font-medium">Back to Topics</span>
                    </button>

                    {/* Header */}
                    <div className="flex items-center justify-between mb-8">
                        <div className="flex items-center gap-5">
                            <div className="flex items-center justify-center w-14 h-14 rounded-xl" style={{ background: style.gradient, boxShadow: '0 8px 20px rgba(0, 0, 0, 0.15)' }}>
                                <span className="text-2xl text-white">📝</span>
                            </div>
                            <div>
                                <h1 className="text-3xl font-bold" style={{ color: '#1F2937', letterSpacing: '-0.5px' }}>{selectedTopic}</h1>
                                <p className="text-gray-500 mt-1">
                                    {(questionsLoading || !hasLoadedQuestions) ? (
                                        <span className="animate-pulse">Loading questions...</span>
                                    ) : (
                                        <span className="flex items-center gap-2">
                                            <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold" style={{ backgroundColor: style.bgLight, color: style.gradient.includes('3B82F6') ? '#3B82F6' : style.gradient.includes('10B981') ? '#10B981' : '#8B5CF6' }}>
                                                {questions.length} question{questions.length !== 1 ? 's' : ''}
                                            </span>
                                            {questions.length > 100 && (
                                                <span className="text-xs text-gray-500 bg-yellow-50 px-2 py-1 rounded-md">
                                                    Large topic - may take a moment to display all questions
                                                </span>
                                            )}
                                        </span>
                                    )}
                                </p>
                            </div>
                        </div>
                        {isAdmin && (
                            <button
                                onClick={handleAddQuestionClick}
                                className="flex items-center gap-2 px-5 py-3 rounded-xl text-white font-semibold transition-all hover:shadow-lg"
                                style={{ background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)', boxShadow: '0 4px 15px rgba(59, 130, 246, 0.3)' }}
                            >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                                </svg>
                                Add Question
                            </button>
                        )}
                    </div>

                    {/* Filters and Sorting */}
                    <div className="bg-white rounded-2xl p-5 mb-8" style={{ boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
                        <div className="flex flex-wrap gap-6 items-center">
                            <div className="flex items-center gap-3">
                                <span className="text-lg">🎯</span>
                                <label className="text-sm font-semibold text-gray-600">Difficulty</label>
                                <select
                                    value={filters.difficulty}
                                    onChange={(e) => setFilters({ ...filters, difficulty: e.target.value })}
                                    className="border-2 border-gray-200 rounded-lg px-4 py-2 font-medium text-gray-700 focus:border-black focus:outline-none transition-colors bg-gray-50 hover:bg-white"
                                >
                                    <option value="">All Levels</option>
                                    <option value="Easy">🟢 Easy</option>
                                    <option value="Medium">🟡 Medium</option>
                                    <option value="Hard">🔴 Hard</option>
                                </select>
                            </div>

                            <div className="w-px h-8 bg-gray-200 hidden md:block"></div>

                            <div className="flex items-center gap-3">
                                <span className="text-lg">📊</span>
                                <label className="text-sm font-semibold text-gray-600">Sort by</label>
                                <select
                                    value={filters.sortBy}
                                    onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
                                    className="border-2 border-gray-200 rounded-lg px-4 py-2 font-medium text-gray-700 focus:border-black focus:outline-none transition-colors bg-gray-50 hover:bg-white"
                                >
                                    <option value="created_at">Date Added</option>
                                    <option value="difficulty">Difficulty</option>
                                    <option value="title">Title</option>
                                </select>
                            </div>

                            <div className="flex items-center gap-3">
                                <span className="text-lg">↕️</span>
                                <label className="text-sm font-semibold text-gray-600">Order</label>
                                <select
                                    value={filters.sortOrder}
                                    onChange={(e) => setFilters({ ...filters, sortOrder: e.target.value })}
                                    className="border-2 border-gray-200 rounded-lg px-4 py-2 font-medium text-gray-700 focus:border-black focus:outline-none transition-colors bg-gray-50 hover:bg-white"
                                >
                                    <option value="desc">Newest First</option>
                                    <option value="asc">Oldest First</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Questions List */}
                    {questionsLoading && (
                        <>
                            <div className="flex items-center justify-center mb-6">
                                <div className="text-center">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-3" style={{ borderColor: '#000000' }}></div>
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

                    {!questionsLoading && !error && hasLoadedQuestions && (
                        <div className="space-y-4">
                            {questions.map((question, index) => {
                                const difficultyStyles = {
                                    'Easy': { bg: '#ECFDF5', color: '#059669', border: '#A7F3D0', icon: '🟢' },
                                    'Medium': { bg: '#FEF3C7', color: '#D97706', border: '#FDE68A', icon: '🟡' },
                                    'Hard': { bg: '#FEE2E2', color: '#DC2626', border: '#FECACA', icon: '🔴' }
                                };
                                const diffStyle = difficultyStyles[question.difficulty] || difficultyStyles['Medium'];

                                return (
                                    <div
                                        key={question.id}
                                        onClick={() => handleQuestionClick(question.id)}
                                        className="group bg-white rounded-2xl cursor-pointer transition-all duration-300 overflow-hidden"
                                        style={{
                                            boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
                                            border: question.solved ? '2px solid #A7F3D0' : '1px solid #E5E7EB',
                                        }}
                                        onMouseEnter={(e) => {
                                            e.currentTarget.style.transform = 'translateY(-2px)';
                                            e.currentTarget.style.boxShadow = '0 12px 24px rgba(0, 0, 0, 0.1)';
                                        }}
                                        onMouseLeave={(e) => {
                                            e.currentTarget.style.transform = 'translateY(0)';
                                            e.currentTarget.style.boxShadow = '0 2px 12px rgba(0, 0, 0, 0.06)';
                                        }}
                                    >
                                        {/* Status indicator bar */}
                                        <div className="h-1" style={{
                                            background: question.solved ? 'linear-gradient(90deg, #000000, #333333)' :
                                                question.attempted ? 'linear-gradient(90deg, #666666, #888888)' :
                                                    '#E5E7EB'
                                        }}></div>

                                        <div className="p-6">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <div className="flex items-center gap-4 mb-3">
                                                        {/* Status icon */}
                                                        <div className="flex items-center justify-center w-10 h-10 rounded-xl" style={{
                                                            backgroundColor: question.solved ? '#ECFDF5' : question.attempted ? '#FEF3C7' : '#F3F4F6',
                                                        }}>
                                                            {question.solved ? (
                                                                <span className="text-xl" title="Solved correctly">✅</span>
                                                            ) : question.attempted ? (
                                                                <span className="text-xl" title="Attempted but not solved">🔄</span>
                                                            ) : (
                                                                <span className="text-xl text-gray-400" title="Not attempted">○</span>
                                                            )}
                                                        </div>
                                                        <h3 className="text-xl font-bold text-gray-800 group-hover:text-gray-900 transition-colors">
                                                            {question.title}
                                                        </h3>
                                                    </div>
                                                    <p className="text-gray-600 mb-4 ml-14">{question.description}</p>
                                                    <div className="flex items-center gap-3 ml-14">
                                                        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold" style={{ backgroundColor: diffStyle.bg, color: diffStyle.color }}>
                                                            {diffStyle.icon} {question.difficulty}
                                                        </span>
                                                        <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-semibold" style={{ backgroundColor: '#EEF2FF', color: '#4F46E5' }}>
                                                            💎 {question.xp_reward} XP
                                                        </span>
                                                        {question.solved && (
                                                            <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-semibold" style={{ backgroundColor: '#F3F4F6', color: '#000000' }}>
                                                                ✓ Solved
                                                            </span>
                                                        )}
                                                        {!question.solved && question.attempted && (
                                                            <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-semibold" style={{ backgroundColor: '#F9FAFB', color: '#666666' }}>
                                                                In Progress
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                                <div className="w-12 h-12 rounded-xl flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all" style={{ backgroundColor: '#F3F4F6' }}>
                                                    <span className="text-xl" style={{ color: '#000000' }}>→</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {!questionsLoading && hasLoadedQuestions && !error && questions.length === 0 && (
                        <div className="bg-white rounded-2xl p-16 text-center" style={{ boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)' }}>
                            <div className="inline-flex items-center justify-center w-24 h-24 rounded-full mb-6" style={{ backgroundColor: '#F3F4F6' }}>
                                <span className="text-5xl">🔍</span>
                            </div>
                            <h3 className="text-2xl font-bold text-gray-900 mb-3">No Questions Found</h3>
                            <p className="text-gray-500 max-w-md mx-auto">
                                No questions match your current filters. Try adjusting the difficulty or sort options.
                            </p>
                            <button
                                onClick={() => setFilters({ difficulty: '', sortBy: 'created_at', sortOrder: 'desc' })}
                                className="mt-6 px-6 py-3 rounded-xl font-semibold text-white transition-all hover:shadow-lg"
                                style={{ background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)' }}
                            >
                                Reset Filters
                            </button>
                        </div>
                    )}

                    {!questionsLoading && error && (
                        <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8">
                            <div className="flex items-start gap-4">
                                <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-red-100">
                                    <span className="text-2xl">⚠️</span>
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-red-800 mb-2">We ran into an issue</h3>
                                    <p className="text-red-600">{error}</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Add Question Modal */}
            {showAddQuestionModal && (
                <div
                    className="fixed inset-0 flex items-center justify-center z-50 p-4 overflow-y-auto"
                    style={{ backgroundColor: 'rgba(0, 0, 0, 0.6)', backdropFilter: 'blur(4px)' }}
                    onClick={handleBackdropClick}
                >
                    <div className="relative max-h-[90vh] overflow-y-auto rounded-2xl">
                        <button
                            onClick={handleCloseModal}
                            className="absolute top-4 right-4 z-10 bg-white rounded-xl p-2.5 hover:bg-gray-100 transition-colors"
                            style={{ boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)' }}
                            aria-label="Close modal"
                        >
                            <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                        <AdminQuestionForm
                            onClose={handleCloseModal}
                            onSuccess={handleQuestionCreated}
                            defaultCategory={selectedCategory}
                            defaultTopic={selectedTopic}
                        />
                    </div>
                </div>
            )}
        </>
    );
}

export default QuestionBank;


