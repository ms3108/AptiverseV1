import React, { useState } from 'react';
import axios from 'axios';
import API_URL from '../config/api';

const AdminQuestionForm = ({ onClose, onSuccess, defaultCategory = '', defaultTopic = '' }) => {
    const [mode, setMode] = useState('single'); // 'single' or 'bulk'
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        category: defaultCategory || '',
        topic: defaultTopic || '',
        sub_topic: '',
        difficulty: '',
        option_a: '',
        option_b: '',
        option_c: '',
        option_d: '',
        correct_answer: '',
        explanation: '',
        xp_reward: 10
    });

    const [errors, setErrors] = useState({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [successMessage, setSuccessMessage] = useState('');
    const [generalError, setGeneralError] = useState('');

    // Bulk upload state
    const [selectedFile, setSelectedFile] = useState(null);
    const [uploadProgress, setUploadProgress] = useState(null);
    const [mergeStrategy, setMergeStrategy] = useState('merge');

    const categories = ['Quants', 'Logical', 'Language'];
    const difficulties = ['Easy', 'Medium', 'Hard'];
    const answerOptions = ['A', 'B', 'C', 'D'];

    const validateField = (name, value) => {
        switch (name) {
            case 'title':
                if (!value.trim()) return 'Title is required';
                if (value.length < 5) return 'Title must be at least 5 characters';
                if (value.length > 500) return 'Title must not exceed 500 characters';
                return '';
            case 'description':
                if (!value.trim()) return 'Description is required';
                if (value.length < 10) return 'Description must be at least 10 characters';
                if (value.length > 5000) return 'Description must not exceed 5000 characters';
                return '';
            case 'category':
                if (!value) return 'Category is required';
                if (!categories.includes(value)) return 'Invalid category';
                return '';
            case 'topic':
                if (!value.trim()) return 'Topic is required';
                if (value.length < 2) return 'Topic must be at least 2 characters';
                if (value.length > 100) return 'Topic must not exceed 100 characters';
                return '';
            case 'sub_topic':
                if (value && value.length > 100) return 'Sub-topic must not exceed 100 characters';
                return '';
            case 'difficulty':
                if (!value) return 'Difficulty is required';
                if (!difficulties.includes(value)) return 'Invalid difficulty';
                return '';
            case 'option_a':
            case 'option_b':
            case 'option_c':
            case 'option_d':
                if (!value.trim()) return `Option ${name.split('_')[1].toUpperCase()} is required`;
                if (value.length < 1) return 'Option must not be empty';
                if (value.length > 1000) return 'Option must not exceed 1000 characters';
                return '';
            case 'correct_answer':
                if (!value) return 'Correct answer is required';
                if (!answerOptions.includes(value)) return 'Invalid answer option';
                return '';
            case 'explanation':
                if (!value.trim()) return 'Explanation is required';
                if (value.length < 10) return 'Explanation must be at least 10 characters';
                if (value.length > 5000) return 'Explanation must not exceed 5000 characters';
                return '';
            case 'xp_reward':
                const xp = parseInt(value);
                if (isNaN(xp)) return 'XP reward must be a number';
                if (xp < 5) return 'XP reward must be at least 5';
                if (xp > 100) return 'XP reward must not exceed 100';
                return '';
            default:
                return '';
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));

        // Clear error for this field when user starts typing
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: '' }));
        }
    };

    const handleBlur = (e) => {
        const { name, value } = e.target;
        const error = validateField(name, value);
        if (error) {
            setErrors(prev => ({ ...prev, [name]: error }));
        }
    };

    const validateForm = () => {
        const newErrors = {};
        Object.keys(formData).forEach(key => {
            const error = validateField(key, formData[key]);
            if (error) {
                newErrors[key] = error;
            }
        });
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Clear previous messages
        setSuccessMessage('');
        setGeneralError('');

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);

        try {
            const token = localStorage.getItem('token');

            if (!token) {
                setGeneralError('You must be logged in to create questions');
                setIsSubmitting(false);
                return;
            }

            const response = await axios.post(
                `${API_URL}/admin/questions/create`,
                formData,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            // Show success message
            setSuccessMessage(response.data.message || 'Question created successfully!');

            // Clear form after successful submission
            setFormData({
                title: '',
                description: '',
                category: defaultCategory || '',
                topic: defaultTopic || '',
                sub_topic: '',
                difficulty: '',
                option_a: '',
                option_b: '',
                option_c: '',
                option_d: '',
                correct_answer: '',
                explanation: '',
                xp_reward: 10
            });

            // Call onSuccess callback with the created question data
            if (onSuccess) {
                onSuccess(response.data);
            }

            // Auto-close after 2 seconds or let parent handle it
            setTimeout(() => {
                setSuccessMessage('');
                if (onClose) {
                    onClose();
                }
            }, 2000);

        } catch (error) {
            console.error('Error creating question:', error);

            if (error.response) {
                // Server responded with error
                const status = error.response.status;
                const data = error.response.data;

                if (status === 401) {
                    setGeneralError('Your session has expired. Please log in again.');
                } else if (status === 403) {
                    setGeneralError('You do not have permission to create questions. Admin privileges required.');
                } else if (status === 400) {
                    // Handle duplicate title or other validation errors
                    if (data.detail && typeof data.detail === 'string') {
                        if (data.detail.includes('title already exists')) {
                            setErrors(prev => ({ ...prev, title: data.detail }));
                        } else {
                            setGeneralError(data.detail);
                        }
                    } else {
                        setGeneralError('Invalid data provided. Please check your inputs.');
                    }
                } else if (status === 422) {
                    // Validation errors from Pydantic
                    if (data.detail && Array.isArray(data.detail)) {
                        const newErrors = {};
                        data.detail.forEach(err => {
                            const field = err.loc[err.loc.length - 1];
                            newErrors[field] = err.msg;
                        });
                        setErrors(newErrors);
                        setGeneralError('Please fix the validation errors below.');
                    } else {
                        setGeneralError('Validation error. Please check your inputs.');
                    }
                } else if (status === 500) {
                    setGeneralError('Server error. Unable to save question. Please try again later.');
                } else {
                    setGeneralError(data.detail || 'An error occurred while creating the question.');
                }
            } else if (error.request) {
                // Network error - no response received
                setGeneralError('Unable to connect to the server. Please check your internet connection and try again.');
            } else {
                // Other errors
                setGeneralError('An unexpected error occurred. Please try again.');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleCancel = () => {
        if (onClose) {
            onClose();
        }
    };

    // Bulk upload handlers
    const handleFileSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (!file.name.endsWith('.json')) {
                setGeneralError('Please select a JSON file');
                setSelectedFile(null);
                return;
            }
            setSelectedFile(file);
            setGeneralError('');
            setSuccessMessage('');
        }
    };

    const handleBulkUpload = async () => {
        if (!selectedFile) {
            setGeneralError('Please select a file to upload');
            return;
        }

        setIsSubmitting(true);
        setGeneralError('');
        setSuccessMessage('');
        setUploadProgress('Uploading...');

        try {
            const token = localStorage.getItem('token');

            if (!token) {
                setGeneralError('You must be logged in to upload questions');
                setIsSubmitting(false);
                setUploadProgress(null);
                return;
            }

            const formData = new FormData();
            formData.append('file', selectedFile);
            formData.append('merge_strategy', mergeStrategy);

            const response = await axios.post(
                `${API_URL}/admin/questions/upload`,
                formData,
                {
                    headers: {
                        Authorization: `Bearer ${token}`,
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            const stats = response.data.stats;
            setSuccessMessage(
                `Upload successful! Added: ${stats.added} out of ${stats.total_in_file} questions. ${stats.errors_count > 0 ? `${stats.errors_count} errors occurred.` : ''}`
            );
            setUploadProgress(null);
            setSelectedFile(null);

            // Reset file input
            const fileInput = document.getElementById('bulk-upload-file');
            if (fileInput) fileInput.value = '';

            // Call onSuccess callback
            if (onSuccess) {
                onSuccess(response.data);
            }

            // Auto-close after 3 seconds
            setTimeout(() => {
                setSuccessMessage('');
                if (onClose) {
                    onClose();
                }
            }, 3000);

        } catch (error) {
            console.error('Error uploading questions:', error);
            setUploadProgress(null);

            if (error.response) {
                const status = error.response.status;
                const data = error.response.data;

                if (status === 401) {
                    setGeneralError('Your session has expired. Please log in again.');
                } else if (status === 403) {
                    setGeneralError('You do not have permission to upload questions. Admin privileges required.');
                } else if (status === 400) {
                    setGeneralError(data.detail || 'Invalid file format or data. Please check your JSON file.');
                } else if (status === 500) {
                    setGeneralError('Server error. Unable to process upload. Please try again later.');
                } else {
                    setGeneralError(data.detail || 'An error occurred while uploading questions.');
                }
            } else if (error.request) {
                setGeneralError('Unable to connect to the server. Please check your internet connection.');
            } else {
                setGeneralError('An unexpected error occurred. Please try again.');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="bg-white rounded-lg shadow-lg max-w-4xl mx-auto">
            <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-2xl font-bold text-gray-900">Add Questions</h2>
                <p className="text-sm text-gray-600 mt-1">Create a single question or upload multiple questions from a JSON file</p>

                {/* Mode Tabs */}
                <div className="flex gap-2 mt-4">
                    <button
                        type="button"
                        onClick={() => {
                            setMode('single');
                            setGeneralError('');
                            setSuccessMessage('');
                        }}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${mode === 'single'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Single Question
                    </button>
                    <button
                        type="button"
                        onClick={() => {
                            setMode('bulk');
                            setGeneralError('');
                            setSuccessMessage('');
                        }}
                        className={`px-4 py-2 rounded-lg font-medium transition-colors ${mode === 'bulk'
                                ? 'bg-blue-600 text-white'
                                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                            }`}
                    >
                        Bulk Upload
                    </button>
                </div>
            </div>

            {mode === 'single' ? (
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Success Message */}
                    {successMessage && (
                        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2">
                            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span>{successMessage}</span>
                        </div>
                    )}

                    {/* General Error Message */}
                    {generalError && (
                        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg flex items-center gap-2">
                            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            <span>{generalError}</span>
                        </div>
                    )}

                    {/* Title */}
                    <div>
                        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                            Title <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="text"
                            id="title"
                            name="title"
                            value={formData.title}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            disabled={isSubmitting}
                            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.title ? 'border-red-500' : 'border-gray-300'
                                }`}
                            placeholder="Enter question title"
                        />
                        {errors.title && <p className="mt-1 text-sm text-red-600">{errors.title}</p>}
                    </div>

                    {/* Description */}
                    <div>
                        <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                            Description <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            id="description"
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            disabled={isSubmitting}
                            rows="4"
                            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.description ? 'border-red-500' : 'border-gray-300'
                                }`}
                            placeholder="Enter the question description"
                        />
                        {errors.description && <p className="mt-1 text-sm text-red-600">{errors.description}</p>}
                    </div>

                    {/* Category, Topic, Sub-topic Row */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* Category */}
                        <div>
                            <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-1">
                                Category <span className="text-red-500">*</span>
                            </label>
                            <select
                                id="category"
                                name="category"
                                value={formData.category}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                disabled={isSubmitting}
                                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.category ? 'border-red-500' : 'border-gray-300'
                                    }`}
                            >
                                <option value="">Select category</option>
                                {categories.map(cat => (
                                    <option key={cat} value={cat}>{cat}</option>
                                ))}
                            </select>
                            {errors.category && <p className="mt-1 text-sm text-red-600">{errors.category}</p>}
                        </div>

                        {/* Topic */}
                        <div>
                            <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-1">
                                Topic <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                id="topic"
                                name="topic"
                                value={formData.topic}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                disabled={isSubmitting}
                                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.topic ? 'border-red-500' : 'border-gray-300'
                                    }`}
                                placeholder="e.g., Profit and Loss"
                            />
                            {errors.topic && <p className="mt-1 text-sm text-red-600">{errors.topic}</p>}
                        </div>

                        {/* Sub-topic */}
                        <div>
                            <label htmlFor="sub_topic" className="block text-sm font-medium text-gray-700 mb-1">
                                Sub-topic
                            </label>
                            <input
                                type="text"
                                id="sub_topic"
                                name="sub_topic"
                                value={formData.sub_topic}
                                onChange={handleChange}
                                onBlur={handleBlur}
                                disabled={isSubmitting}
                                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.sub_topic ? 'border-red-500' : 'border-gray-300'
                                    }`}
                                placeholder="Optional"
                            />
                            {errors.sub_topic && <p className="mt-1 text-sm text-red-600">{errors.sub_topic}</p>}
                        </div>
                    </div>

                    {/* Difficulty */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Difficulty <span className="text-red-500">*</span>
                        </label>
                        <div className="flex gap-4">
                            {difficulties.map(diff => (
                                <label key={diff} className="flex items-center cursor-pointer">
                                    <input
                                        type="radio"
                                        name="difficulty"
                                        value={diff}
                                        checked={formData.difficulty === diff}
                                        onChange={handleChange}
                                        disabled={isSubmitting}
                                        className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500"
                                    />
                                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${diff === 'Easy' ? 'bg-green-100 text-green-800' :
                                            diff === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                                'bg-red-100 text-red-800'
                                        }`}>
                                        {diff}
                                    </span>
                                </label>
                            ))}
                        </div>
                        {errors.difficulty && <p className="mt-1 text-sm text-red-600">{errors.difficulty}</p>}
                    </div>

                    {/* Options */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-gray-900">Answer Options</h3>

                        {answerOptions.map(option => {
                            const fieldName = `option_${option.toLowerCase()}`;
                            return (
                                <div key={option}>
                                    <label htmlFor={fieldName} className="block text-sm font-medium text-gray-700 mb-1">
                                        Option {option} <span className="text-red-500">*</span>
                                    </label>
                                    <textarea
                                        id={fieldName}
                                        name={fieldName}
                                        value={formData[fieldName]}
                                        onChange={handleChange}
                                        onBlur={handleBlur}
                                        disabled={isSubmitting}
                                        rows="2"
                                        className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors[fieldName] ? 'border-red-500' : 'border-gray-300'
                                            }`}
                                        placeholder={`Enter option ${option}`}
                                    />
                                    {errors[fieldName] && <p className="mt-1 text-sm text-red-600">{errors[fieldName]}</p>}
                                </div>
                            );
                        })}
                    </div>

                    {/* Correct Answer */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Correct Answer <span className="text-red-500">*</span>
                        </label>
                        <div className="flex gap-4">
                            {answerOptions.map(option => (
                                <label key={option} className="flex items-center cursor-pointer">
                                    <input
                                        type="radio"
                                        name="correct_answer"
                                        value={option}
                                        checked={formData.correct_answer === option}
                                        onChange={handleChange}
                                        disabled={isSubmitting}
                                        className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500"
                                    />
                                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                                        {option}
                                    </span>
                                </label>
                            ))}
                        </div>
                        {errors.correct_answer && <p className="mt-1 text-sm text-red-600">{errors.correct_answer}</p>}
                    </div>

                    {/* Explanation */}
                    <div>
                        <label htmlFor="explanation" className="block text-sm font-medium text-gray-700 mb-1">
                            Explanation <span className="text-red-500">*</span>
                        </label>
                        <textarea
                            id="explanation"
                            name="explanation"
                            value={formData.explanation}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            disabled={isSubmitting}
                            rows="4"
                            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.explanation ? 'border-red-500' : 'border-gray-300'
                                }`}
                            placeholder="Explain why the correct answer is correct"
                        />
                        {errors.explanation && <p className="mt-1 text-sm text-red-600">{errors.explanation}</p>}
                    </div>

                    {/* XP Reward */}
                    <div>
                        <label htmlFor="xp_reward" className="block text-sm font-medium text-gray-700 mb-1">
                            XP Reward <span className="text-red-500">*</span>
                        </label>
                        <input
                            type="number"
                            id="xp_reward"
                            name="xp_reward"
                            value={formData.xp_reward}
                            onChange={handleChange}
                            onBlur={handleBlur}
                            disabled={isSubmitting}
                            min="5"
                            max="100"
                            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${errors.xp_reward ? 'border-red-500' : 'border-gray-300'
                                }`}
                        />
                        <p className="mt-1 text-sm text-gray-500">XP reward must be between 5 and 100</p>
                        {errors.xp_reward && <p className="mt-1 text-sm text-red-600">{errors.xp_reward}</p>}
                    </div>

                    {/* Form Actions */}
                    <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                        <button
                            type="button"
                            onClick={handleCancel}
                            disabled={isSubmitting}
                            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {isSubmitting ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                    Creating...
                                </>
                            ) : (
                                'Create Question'
                            )}
                        </button>
                    </div>
                </form>
            ) : (
                <div className="p-6 space-y-6">
                    {/* Success Message */}
                    {successMessage && (
                        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg flex items-center gap-2">
                            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span>{successMessage}</span>
                        </div>
                    )}

                    {/* General Error Message */}
                    {generalError && (
                        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg flex items-center gap-2">
                            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                            <span>{generalError}</span>
                        </div>
                    )}

                    {/* Upload Progress */}
                    {uploadProgress && (
                        <div className="bg-blue-50 border border-blue-200 text-blue-800 px-4 py-3 rounded-lg flex items-center gap-2">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                            <span>{uploadProgress}</span>
                        </div>
                    )}

                    {/* Instructions */}
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <h3 className="font-semibold text-blue-900 mb-2">📄 JSON File Format</h3>
                        <p className="text-sm text-blue-800 mb-2">
                            Upload a JSON file containing an array of questions. Each question must have these fields:
                        </p>
                        <ul className="text-sm text-blue-800 list-disc list-inside space-y-1">
                            <li>title, description, difficulty, topic</li>
                            <li>option_a, option_b, option_c, option_d</li>
                            <li>correct_answer (A, B, C, or D)</li>
                            <li>explanation, xp_reward</li>
                        </ul>
                        <p className="text-sm text-blue-800 mt-2">
                            See <code className="bg-blue-100 px-1 rounded">QUESTION_UPLOAD_FORMAT.md</code> for detailed format and examples.
                        </p>
                    </div>

                    {/* Merge Strategy */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Merge Strategy
                        </label>
                        <div className="space-y-2">
                            <label className="flex items-start cursor-pointer">
                                <input
                                    type="radio"
                                    name="merge_strategy"
                                    value="merge"
                                    checked={mergeStrategy === 'merge'}
                                    onChange={(e) => setMergeStrategy(e.target.value)}
                                    disabled={isSubmitting}
                                    className="mt-1 mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Merge (Recommended)</span>
                                    <p className="text-sm text-gray-600">Update existing questions and add new ones</p>
                                </div>
                            </label>
                            <label className="flex items-start cursor-pointer">
                                <input
                                    type="radio"
                                    name="merge_strategy"
                                    value="append"
                                    checked={mergeStrategy === 'append'}
                                    onChange={(e) => setMergeStrategy(e.target.value)}
                                    disabled={isSubmitting}
                                    className="mt-1 mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-gray-900">Append</span>
                                    <p className="text-sm text-gray-600">Add all questions as new (may create duplicates)</p>
                                </div>
                            </label>
                            <label className="flex items-start cursor-pointer">
                                <input
                                    type="radio"
                                    name="merge_strategy"
                                    value="replace"
                                    checked={mergeStrategy === 'replace'}
                                    onChange={(e) => setMergeStrategy(e.target.value)}
                                    disabled={isSubmitting}
                                    className="mt-1 mr-3 h-4 w-4 text-blue-600 focus:ring-blue-500"
                                />
                                <div>
                                    <span className="font-medium text-red-900">Replace All</span>
                                    <p className="text-sm text-red-600">⚠️ Delete ALL existing questions and add new ones</p>
                                </div>
                            </label>
                        </div>
                    </div>

                    {/* File Upload */}
                    <div>
                        <label htmlFor="bulk-upload-file" className="block text-sm font-medium text-gray-700 mb-2">
                            Select JSON File
                        </label>
                        <div className="flex items-center gap-3">
                            <input
                                type="file"
                                id="bulk-upload-file"
                                accept=".json"
                                onChange={handleFileSelect}
                                disabled={isSubmitting}
                                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 disabled:opacity-50"
                            />
                        </div>
                        {selectedFile && (
                            <p className="mt-2 text-sm text-gray-600">
                                Selected: <span className="font-medium">{selectedFile.name}</span> ({(selectedFile.size / 1024).toFixed(2)} KB)
                            </p>
                        )}
                    </div>

                    {/* Form Actions */}
                    <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
                        <button
                            type="button"
                            onClick={handleCancel}
                            disabled={isSubmitting}
                            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            Cancel
                        </button>
                        <button
                            type="button"
                            onClick={handleBulkUpload}
                            disabled={isSubmitting || !selectedFile}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {isSubmitting ? (
                                <>
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                                    Uploading...
                                </>
                            ) : (
                                <>
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                                    </svg>
                                    Upload Questions
                                </>
                            )}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AdminQuestionForm;
