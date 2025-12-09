import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Navigation from './Navigation';

function PracticeSet() {
    const navigate = useNavigate();
    const [questions, setQuestions] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState('');
    const [isAnswered, setIsAnswered] = useState(false);
    const [answerResult, setAnswerResult] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [startTime, setStartTime] = useState(null);
    const [practiceComplete, setPracticeComplete] = useState(false);
    const [score, setScore] = useState({ correct: 0, total: 0 });
    const [userPreference, setUserPreference] = useState(10);

    useEffect(() => {
        fetchPracticeSet();
    }, []);

    const fetchPracticeSet = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/daily-practice`, {
                headers: { Authorization: `Bearer ${token}` }
            });

            // Check if practice is already completed today
            if (response.data.already_completed) {
                setError(response.data.message);
                setLoading(false);
                return;
            }

            setQuestions(response.data.questions);
            setUserPreference(response.data.user_preference || 10);
            setLoading(false);
            setStartTime(Date.now());
        } catch (err) {
            setError('Failed to load practice questions');
            setLoading(false);
        }
    };

    const handleAnswerSelect = (option) => {
        if (!isAnswered) {
            setSelectedAnswer(option);
        }
    };

    const handleSubmitAnswer = async () => {
        if (!selectedAnswer) {
            alert('Please select an answer');
            return;
        }

        const timeTaken = (Date.now() - startTime) / 1000; // in seconds
        const currentQuestion = questions[currentQuestionIndex];

        try {
            const token = localStorage.getItem('token');
            const response = await axios.post(
                `${API_URL}/submit-answer`,
                {
                    question_id: currentQuestion.id,
                    user_answer: selectedAnswer,
                    time_taken_seconds: timeTaken
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            setAnswerResult(response.data);
            setIsAnswered(true);

            // Update score
            if (response.data.is_correct) {
                setScore(prev => ({ correct: prev.correct + 1, total: prev.total + 1 }));
            } else {
                setScore(prev => ({ ...prev, total: prev.total + 1 }));
            }

            // Show new badges if earned
            if (response.data.new_badges && response.data.new_badges.length > 0) {
                const badgeNames = response.data.new_badges.map(b => b.name).join(', ');
                setTimeout(() => {
                    alert(`🎉 Congratulations! You earned: ${badgeNames}`);
                }, 500);
            }
        } catch (err) {
            alert('Error submitting answer: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleNextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
            setSelectedAnswer('');
            setIsAnswered(false);
            setAnswerResult(null);
            setStartTime(Date.now());
        } else {
            setPracticeComplete(true);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center min-h-screen">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    if (error) {
        const isCompletionMessage = error.includes("already completed");
        return (
            <div className="max-w-2xl mx-auto mt-8">
                <div className={`${isCompletionMessage
                    ? 'bg-green-50 border border-green-200'
                    : 'bg-red-50 border border-red-200'} rounded-lg p-6`}>
                    {isCompletionMessage ? (
                        <div className="text-center">
                            <div className="text-6xl mb-4">🎉</div>
                            <h2 className="text-2xl font-bold text-green-800 mb-2">
                                Practice Complete!
                            </h2>
                            <p className="text-green-700 mb-6">
                                {error}
                            </p>
                            <button
                                onClick={() => navigate('/dashboard')}
                                className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-semibold"
                            >
                                Back to Dashboard
                            </button>
                        </div>
                    ) : (
                        <div className="text-red-700">
                            {error}
                        </div>
                    )}
                </div>
            </div>
        );
    }

    if (practiceComplete) {
        return (
            <div className="max-w-2xl mx-auto mt-8">
                <div className="bg-white shadow-lg rounded-lg p-8 text-center">
                    <div className="text-6xl mb-4">🎉</div>
                    <h2 className="text-3xl font-bold text-gray-800 mb-4">
                        Practice Complete!
                    </h2>
                    <p className="text-xl text-gray-600 mb-6">
                        You answered {score.correct} out of {score.total} questions correctly
                    </p>
                    <div className="bg-gradient-to-r from-blue-500 to-blue-700 text-white rounded-lg p-6 mb-6">
                        <p className="text-lg mb-2">Your Performance</p>
                        <p className="text-4xl font-bold">
                            {Math.round((score.correct / score.total) * 100)}%
                        </p>
                        {answerResult && (
                            <div className="mt-4 text-sm">
                                <p>Current Level: {answerResult.current_level}</p>
                                <p>Total XP: {answerResult.total_xp}</p>
                                <p>Current Streak: {answerResult.current_streak} days 🔥</p>
                            </div>
                        )}
                    </div>
                    <button
                        onClick={() => window.location.href = '/dashboard'}
                        className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    if (questions.length === 0) {
        return (
            <div className="max-w-2xl mx-auto mt-8">
                <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded">
                    No questions available for practice at the moment.
                </div>
            </div>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];
    const options = [
        { label: 'A', text: currentQuestion.option_a },
        { label: 'B', text: currentQuestion.option_b },
        { label: 'C', text: currentQuestion.option_c },
        { label: 'D', text: currentQuestion.option_d }
    ];

    return (
        <>
            <Navigation />
            <div className="max-w-4xl mx-auto mt-8 px-4">
                {/* AI-Powered Practice Header */}
                <div className="mb-6 bg-white rounded-xl shadow-sm border" style={{ borderColor: '#E2E8F0' }}>
                    <div className="p-5">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{
                                    background: 'linear-gradient(135deg, #1E88E5 0%, #0D47A1 100%)'
                                }}>
                                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 className="text-lg font-bold text-gray-900">
                                        Personalized Practice Set
                                    </h3>
                                    <p className="text-sm text-gray-600">
                                        {questions.length} Digital Assistant–Curated Questions to Elevate Your Skills
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => navigate('/settings')}
                                className="px-4 py-2 text-sm font-semibold rounded-lg transition-all border-2 hover:shadow-md"
                                style={{
                                    borderColor: '#1E88E5',
                                    color: '#1E88E5',
                                    backgroundColor: 'white'
                                }}
                                onMouseEnter={(e) => {
                                    e.target.style.backgroundColor = '#E3F2FD';
                                }}
                                onMouseLeave={(e) => {
                                    e.target.style.backgroundColor = 'white';
                                }}
                            >
                                Adjust Questions
                            </button>
                        </div>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-6">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">
                            Question {currentQuestionIndex + 1} of {questions.length}
                        </span>
                        <span className="text-sm font-medium text-gray-700">
                            Score: {score.correct}/{score.total}
                        </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                            className="h-2 rounded-full transition-all duration-300"
                            style={{
                                width: `${((currentQuestionIndex + 1) / questions.length) * 100}%`,
                                background: 'linear-gradient(135deg, #1E88E5 0%, #0D47A1 100%)'
                            }}
                        ></div>
                    </div>
                </div>

                {/* Question Card */}
                <div className="bg-white shadow-lg rounded-lg p-6 mb-6">
                    {/* Question Header */}
                    <div className="flex items-center justify-between mb-4">
                        <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm font-semibold rounded">
                            {currentQuestion.topic}
                        </span>
                        <span className={`inline-block px-3 py-1 text-sm font-semibold rounded ${currentQuestion.difficulty === 'Easy' ? 'bg-green-100 text-green-800' :
                            currentQuestion.difficulty === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                                'bg-red-100 text-red-800'
                            }`}>
                            {currentQuestion.difficulty}
                        </span>
                    </div>

                    {/* Question Title and Description */}
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">
                        {currentQuestion.title}
                    </h3>
                    <p className="text-gray-600 mb-6">
                        {currentQuestion.description}
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
                        <div className={`mt-6 p-4 rounded-lg ${answerResult.is_correct ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
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
                                    <span className="ml-4 text-sm font-semibold text-blue-700">
                                        +{answerResult.xp_earned} XP
                                    </span>
                                )}
                            </div>
                            <p className="text-gray-700 text-sm">
                                <strong>Explanation:</strong> {answerResult.explanation}
                            </p>
                        </div>
                    )}

                    {/* Action Buttons */}
                    <div className="mt-6 flex justify-end space-x-3">
                        {!isAnswered ? (
                            <button
                                onClick={handleSubmitAnswer}
                                disabled={!selectedAnswer}
                                className={`px-6 py-2 rounded-lg font-semibold transition ${selectedAnswer
                                    ? 'bg-blue-600 text-white hover:bg-blue-700'
                                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                    }`}
                            >
                                Submit Answer
                            </button>
                        ) : (
                            <button
                                onClick={handleNextQuestion}
                                className="px-6 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition"
                            >
                                {currentQuestionIndex < questions.length - 1 ? 'Next Question →' : 'Finish Practice'}
                            </button>
                        )}
                    </div>
                </div>

                {/* XP Reward Info */}
                <div className="text-center text-sm text-gray-500">
                    💎 Earn {currentQuestion.xp_reward} XP for solving this question
                </div>
            </div>
        </>
    );
}

export default PracticeSet;


