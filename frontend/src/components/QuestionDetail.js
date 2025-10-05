import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';
import axios from 'axios';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import DiscussionSection from './DiscussionSection';

function QuestionDetail() {
    const { questionId } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const [question, setQuestion] = useState(null);
    const [selectedAnswer, setSelectedAnswer] = useState('');
    const [isAnswered, setIsAnswered] = useState(false);
    const [answerResult, setAnswerResult] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState('');
    const [startTime, setStartTime] = useState(Date.now());

    // Get navigation state if available
    const navigationState = location.state;

    useEffect(() => {
        fetchQuestionDetail();
    }, [questionId]);

    const fetchQuestionDetail = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(
                `${API_URL}/question-bank/question/${questionId}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setQuestion(response.data);
            setSelectedAnswer('');
            setIsAnswered(false);
            setAnswerResult(null);
            setSubmitError('');
            setStartTime(Date.now());
            setLoading(false);
        } catch (err) {
            console.error('Failed to load question', err);
            setLoading(false);
        }
    };

    const handleAnswerSelect = (option) => {
        if (!isAnswered && !isSubmitting) {
            setSelectedAnswer(option);
        }
    };

    const handleSubmitAnswer = async () => {
        if (!selectedAnswer) {
            alert('Please select an answer');
            return;
        }

        const timeTaken = (Date.now() - startTime) / 1000;

        try {
            setSubmitError('');
            setIsSubmitting(true);
            const token = localStorage.getItem('token');
            const response = await axios.post(
                `${API_URL}/submit-answer`,
                {
                    question_id: question.id,
                    user_answer: selectedAnswer,
                    time_taken_seconds: timeTaken
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            setAnswerResult(response.data);
            setIsAnswered(true);
            setQuestion((prev) => {
                if (!prev) {
                    return prev;
                }
                const attemptCount = (prev.attempt_count || 0) + 1;
                return {
                    ...prev,
                    attempt_count: attemptCount,
                    solved: prev.solved || response.data.is_correct,
                    correct_answer: response.data.correct_answer || prev.correct_answer,
                    explanation: response.data.explanation || prev.explanation
                };
            });
        } catch (err) {
            const message = err.response?.data?.detail || err.message || 'Unknown error';
            setSubmitError(`Error submitting answer: ${message}`);
        }
        finally {
            setIsSubmitting(false);
        }
    };

    const handleBackNavigation = () => {
        // Always go back in history - now works because QuestionBank uses URL params
        navigate(-1);
    };

    const getDifficultyColor = (difficulty) => {
        switch (difficulty) {
            case 'Easy': return 'bg-green-100 text-green-800';
            case 'Medium': return 'bg-yellow-100 text-yellow-800';
            case 'Hard': return 'bg-red-100 text-red-800';
            default: return 'bg-gray-100 text-gray-800';
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (!question) {
        return (
            <div className="max-w-2xl mx-auto mt-8 px-4">
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                    Question not found
                </div>
            </div>
        );
    }

    const options = [
        { label: 'A', text: question.option_a },
        { label: 'B', text: question.option_b },
        { label: 'C', text: question.option_c },
        { label: 'D', text: question.option_d }
    ];

    return (
        <div className="max-w-4xl mx-auto mt-8 px-4 pb-8">
            <div className="mb-6">
                <button
                    onClick={handleBackNavigation}
                    className="text-blue-600 hover:text-blue-800 flex items-center"
                >
                    ← Back to Questions
                </button>
            </div>

            <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
                {/* Question Header */}
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm font-semibold rounded">
                            {question.topic}
                        </span>
                        <span className={`inline-block px-3 py-1 text-sm font-semibold rounded ${getDifficultyColor(question.difficulty)}`}>
                            {question.difficulty}
                        </span>
                        {question.solved && (
                            <span className="text-green-600 text-xl" title="Solved">✓</span>
                        )}
                    </div>
                    <span className="text-sm text-gray-500">
                        💎 {question.xp_reward} XP
                    </span>
                </div>

                {/* Attempt Count */}
                {question.attempt_count > 0 && (
                    <div className="mb-4 text-sm text-gray-600">
                        Attempts: {question.attempt_count}
                    </div>
                )}

                {/* Question Title and Description */}
                <h2 className="text-2xl font-bold text-gray-800 mb-3">
                    {question.title}
                </h2>
                <p className="text-gray-600 mb-6">
                    {question.description}
                </p>

                {/* Answer Options */}
                <div className="space-y-3">
                    {options.map((option) => (
                        <button
                            key={option.label}
                            onClick={() => handleAnswerSelect(option.label)}
                            disabled={isAnswered}
                            className={`w-full text-left p-4 rounded-lg border-2 transition-all ${isAnswered
                                ? option.label === answerResult?.correct_answer
                                    ? 'border-green-500 bg-green-50'
                                    : option.label === selectedAnswer
                                        ? 'border-red-500 bg-red-50'
                                        : 'border-gray-200 bg-gray-50'
                                : selectedAnswer === option.label
                                    ? 'border-blue-500 bg-blue-50'
                                    : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                                } ${isAnswered ? 'cursor-not-allowed' : 'cursor-pointer'}`}
                        >
                            <div className="flex items-center">
                                <span className="font-bold mr-3 text-lg">{option.label}.</span>
                                <span className="text-gray-800">{option.text}</span>
                                {isAnswered && option.label === answerResult?.correct_answer && (
                                    <span className="ml-auto text-green-600">✓</span>
                                )}
                                {isAnswered && option.label === selectedAnswer && option.label !== answerResult?.correct_answer && (
                                    <span className="ml-auto text-red-600">✗</span>
                                )}
                            </div>
                        </button>
                    ))}
                </div>

                {/* Explanation (shown after answering) */}
                {isAnswered && answerResult && (
                    <div className={`mt-6 p-4 rounded-lg ${answerResult.is_correct
                        ? 'bg-green-50 border border-green-200'
                        : 'bg-red-50 border border-red-200'
                        }`}>
                        <div className="flex items-center mb-2">
                            <span className="text-2xl mr-2">
                                {answerResult.is_correct ? '✅' : '❌'}
                            </span>
                            <span className={`font-bold ${answerResult.is_correct ? 'text-green-800' : 'text-red-800'
                                }`}>
                                {answerResult.is_correct ? 'Correct!' : 'Incorrect'}
                            </span>
                            {answerResult.xp_earned > 0 && (
                                <span className="ml-4 text-sm font-semibold text-purple-700">
                                    +{answerResult.xp_earned} XP
                                </span>
                            )}
                        </div>
                        <p className="text-gray-700 text-sm">
                            <strong>Explanation:</strong> {answerResult.explanation}
                        </p>
                    </div>
                )}

                {/* Show explanation if already solved */}
                {question.solved && !isAnswered && question.explanation && (
                    <div className="mt-6 p-4 rounded-lg bg-blue-50 border border-blue-200">
                        <p className="text-gray-700 text-sm">
                            <strong>✓ You've already solved this question!</strong>
                        </p>
                        <p className="text-gray-700 text-sm mt-2">
                            <strong>Correct Answer:</strong> {question.correct_answer}
                        </p>
                        <p className="text-gray-700 text-sm mt-2">
                            <strong>Explanation:</strong> {question.explanation}
                        </p>
                    </div>
                )}

                {/* Action Buttons */}
                <div className="mt-6 flex justify-end space-x-3">
                    {!isAnswered && !question.solved ? (
                        <button
                            onClick={handleSubmitAnswer}
                            disabled={!selectedAnswer || isSubmitting}
                            className={`px-6 py-2 rounded-lg font-semibold transition flex items-center justify-center gap-2 ${selectedAnswer && !isSubmitting
                                ? 'bg-blue-600 text-white hover:bg-blue-700'
                                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                }`}
                            aria-busy={isSubmitting}
                        >
                            {isSubmitting ? (
                                <>
                                    <span className="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                                    <span>Submitting…</span>
                                </>
                            ) : (
                                'Submit Answer'
                            )}
                        </button>
                    ) : (
                        <button
                            onClick={handleBackNavigation}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                        >
                            Back to Questions
                        </button>
                    )}
                </div>
            </div>

            {/* Community Discussion Section */}
            <DiscussionSection
                questionId={parseInt(questionId)}
                isSolved={question.solved || isAnswered}
            />
        </div>
    );
    {
        submitError && (
            <div className="mt-4 p-3 rounded bg-red-50 border border-red-200 text-sm text-red-700">
                {submitError}
            </div>
        )
    }

}

export default QuestionDetail;


