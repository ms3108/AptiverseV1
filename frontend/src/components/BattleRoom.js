import React, { useState, useEffect, useRef } from 'react';
import API_URL from '../config/api';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import Navigation from './Navigation';

function BattleRoom() {
    const { roomCode } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const [battleInfo, setBattleInfo] = useState(null);
    const [battleStatus, setBattleStatus] = useState('waiting'); // waiting, in_progress, completed
    const [currentQuestion, setCurrentQuestion] = useState(null);
    const [questionNumber, setQuestionNumber] = useState(0);
    const [totalQuestions, setTotalQuestions] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    const [timeLeft, setTimeLeft] = useState(60);
    const [timePerQuestion, setTimePerQuestion] = useState(60);  // Dynamic time limit
    const [leaderboard, setLeaderboard] = useState([]);
    const [answerResult, setAnswerResult] = useState(null);
    const [participants, setParticipants] = useState([]);
    const [isCreator, setIsCreator] = useState(false);
    const [shareableLink, setShareableLink] = useState('');

    const ws = useRef(null);
    const timerRef = useRef(null);
    const questionStartTime = useRef(null);

    useEffect(() => {
        fetchBattleInfo();
        // WebSocket will be connected after successfully joining/verifying participant status

        return () => {
            if (ws.current) {
                ws.current.close();
            }
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        };
    }, [roomCode]);

    const fetchBattleInfo = async () => {
        console.log('🔍 Fetching battle info for room:', roomCode);
        try {
            const token = localStorage.getItem('token');
            console.log('🔑 Token exists:', !!token);
            const response = await axios.get(`${API_URL}/battles/${roomCode}/info`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            console.log('✅ Battle info received:', response.data);

            console.log('👤 User from AuthContext:', user);
            if (!user) {
                alert('Please log in again');
                navigate('/login');
                return;
            }

            const currentUserId = user.id;
            console.log('🆔 Current user ID:', currentUserId);

            // Check if current user is a participant
            const isParticipant = response.data.participants.some(p => p.user_id === currentUserId);
            console.log('✓ Is participant:', isParticipant);

            if (!isParticipant) {
                // Auto-join if not a participant
                try {
                    await axios.post(
                        `${API_URL}/battles/${roomCode}/join`,
                        {},
                        { headers: { Authorization: `Bearer ${token}` } }
                    );
                    // Refetch battle info after joining
                    const updatedResponse = await axios.get(`${API_URL}/battles/${roomCode}/info`, {
                        headers: { Authorization: `Bearer ${token}` }
                    });
                    setBattleInfo(updatedResponse.data);
                    setBattleStatus(updatedResponse.data.status);
                    setParticipants(updatedResponse.data.participants);
                    setTotalQuestions(updatedResponse.data.num_questions);
                    setTimePerQuestion(updatedResponse.data.time_per_question || 60);
                    setTimeLeft(updatedResponse.data.time_per_question || 60);

                    // Connect WebSocket AFTER successfully joining
                    console.log('✅ Successfully joined, now connecting WebSocket...');
                    connectWebSocket();
                } catch (joinError) {
                    console.error('Failed to join battle', joinError);
                    alert(joinError.response?.data?.detail || 'Failed to join battle room');
                    navigate('/dashboard');
                    return;
                }
            } else {
                setBattleInfo(response.data);
                setBattleStatus(response.data.status);
                setParticipants(response.data.participants);
                setTotalQuestions(response.data.num_questions);
                setTimePerQuestion(response.data.time_per_question || 60);
                setTimeLeft(response.data.time_per_question || 60);

                // Connect WebSocket AFTER confirming participant status
                console.log('✅ Already a participant, connecting WebSocket...');
                connectWebSocket();
            }

            setIsCreator(response.data.creator_id === currentUserId);
            const frontendUrl = window.location.origin;
            setShareableLink(`${frontendUrl}/battle/${roomCode}`);
        } catch (error) {
            console.error('Failed to fetch battle info', error);
            console.error('Error details:', error.response?.data);
            console.error('Error status:', error.response?.status);
            const errorMessage = error.response?.data?.detail || error.message || 'Battle room not found';
            alert(errorMessage);
            navigate('/dashboard');
        }
    };

    const connectWebSocket = () => {
        const token = localStorage.getItem('token');
        // Convert HTTP API URL to WebSocket URL
        const wsProtocol = API_URL.startsWith('https') ? 'wss' : 'ws';
        const wsHost = API_URL.replace(/^https?:\/\//, '');
        const wsUrl = `${wsProtocol}://${wsHost}/ws/battle/${roomCode}?token=${token}`;
        console.log('🔌 Connecting to WebSocket:', wsUrl);

        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            console.log('✅ WebSocket connected to battle room');
        };

        ws.current.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };

        ws.current.onclose = (event) => {
            console.log('🔌 WebSocket closed:', event.code, event.reason);
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log('📨 Received WebSocket message:', data.type, data);

            switch (data.type) {
                case 'user_joined':
                    console.log(`✅ ${data.username} joined the battle`);
                    setParticipants(prev => {
                        // Check if user already exists to prevent duplicates
                        const exists = prev.some(p => p.user_id === data.user_id);
                        if (exists) {
                            console.log(`⚠️ User ${data.username} already in participants list`);
                            return prev;
                        }
                        return [...prev, {
                            user_id: data.user_id,
                            username: data.username,
                            score: 0,
                            correct_answers: 0
                        }];
                    });
                    break;

                case 'battle_started':
                    console.log('🎮 BATTLE STARTED MESSAGE RECEIVED!');
                    console.log('🎮 Current battle status:', battleStatus);
                    console.log('🎮 Changing status to in_progress');
                    setBattleStatus('in_progress');
                    console.log('🎮 Status change triggered');
                    break;

                case 'question':
                    console.log('❓ Received question:', data.question_number, '/', data.total_questions);
                    setCurrentQuestion(data.question);
                    setQuestionNumber(data.question_number);
                    setTotalQuestions(data.total_questions);
                    setSelectedAnswer(null);
                    setAnswerResult(null);
                    setTimeLeft(timePerQuestion);
                    questionStartTime.current = Date.now();
                    startTimer();
                    break;

                case 'answer_result':
                    setAnswerResult(data);
                    if (timerRef.current) {
                        clearInterval(timerRef.current);
                    }
                    break;

                case 'leaderboard':
                    setLeaderboard(data.leaderboard);
                    break;

                case 'battle_completed':
                    setBattleStatus('completed');
                    setLeaderboard(data.final_leaderboard);
                    if (timerRef.current) {
                        clearInterval(timerRef.current);
                    }
                    break;

                case 'user_left':
                    console.log(`${data.username} left the battle`);
                    break;

                default:
                    break;
            }
        };

        ws.current.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        ws.current.onclose = () => {
            console.log('Disconnected from battle room');
        };
    };

    const startTimer = () => {
        if (timerRef.current) {
            clearInterval(timerRef.current);
        }

        timerRef.current = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    clearInterval(timerRef.current);
                    // Auto-submit if time runs out
                    if (!answerResult && selectedAnswer) {
                        handleSubmitAnswer();
                    }
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
    };

    const handleStartBattle = () => {
        console.log('🚀 Start Battle button clicked!');
        console.log('📡 WebSocket exists:', !!ws.current);
        console.log('📡 WebSocket ready state:', ws.current?.readyState);
        console.log('📡 WebSocket OPEN constant:', WebSocket.OPEN);

        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            console.log('✅ Sending start_battle message...');
            ws.current.send(JSON.stringify({ type: 'start_battle' }));
        } else {
            console.error('❌ WebSocket not connected!');
            alert('WebSocket not connected. Please refresh the page.');
        }
    };

    const handleSubmitAnswer = () => {
        if (!selectedAnswer || answerResult) return;

        const timeTaken = (Date.now() - questionStartTime.current) / 1000;

        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({
                type: 'submit_answer',
                question_id: currentQuestion.id,
                answer: selectedAnswer,
                time_taken: timeTaken
            }));
        }

        if (timerRef.current) {
            clearInterval(timerRef.current);
        }
    };

    const copyShareableLink = () => {
        navigator.clipboard.writeText(shareableLink);
        alert('Link copied to clipboard!');
    };

    // Waiting Room View
    if (battleStatus === 'waiting') {
        return (
            <>
                <Navigation />
                <div className="min-h-screen" style={{ backgroundColor: '#F8FAFF', padding: '40px 20px' }}>
                    <div className="max-w-4xl mx-auto">
                        {/* Header */}
                        <div className="text-center mb-8">
                            <h1 className="text-4xl font-black mb-2" style={{
                                background: 'linear-gradient(135deg, #1565C0 0%, #1E88E5 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                letterSpacing: '-1px'
                            }}>
                                ⚔️ Battle Room
                            </h1>
                            <p className="text-lg font-medium" style={{ color: '#64748B' }}>
                                Room Code: <span style={{ color: '#000000', fontWeight: 'bold' }}>{roomCode}</span>
                            </p>
                        </div>

                        {/* Battle Info */}
                        {battleInfo && (
                            <div className="bg-white neomorph p-8 mb-6" style={{ borderRadius: '12px' }}>
                                <h2 className="text-2xl font-bold mb-4" style={{ color: '#1A202C' }}>
                                    Battle Configuration
                                </h2>
                                <div className="grid grid-cols-3 gap-4 mb-6">
                                    <div>
                                        <p className="text-sm font-semibold mb-1" style={{ color: '#64748B' }}>Topic</p>
                                        <p className="text-xl font-bold" style={{ color: '#000000' }}>{battleInfo.topic}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold mb-1" style={{ color: '#64748B' }}>Questions</p>
                                        <p className="text-xl font-bold" style={{ color: '#42A5F5' }}>{battleInfo.num_questions}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold mb-1" style={{ color: '#64748B' }}>Time/Question</p>
                                        <p className="text-xl font-bold" style={{ color: '#0D47A1' }}>{timePerQuestion}s</p>
                                    </div>
                                </div>

                                {/* Shareable Link */}
                                <div className="mb-6">
                                    <p className="text-sm font-semibold mb-2" style={{ color: '#64748B' }}>Share this link with others:</p>
                                    <div className="flex gap-2">
                                        <input
                                            type="text"
                                            value={shareableLink}
                                            readOnly
                                            className="flex-1 px-4 py-2 border rounded-lg"
                                            style={{ backgroundColor: '#F8FAFF', borderColor: '#E2E8F0', color: '#1A202C' }}
                                        />
                                        <button
                                            onClick={copyShareableLink}
                                            className="px-6 py-2 font-semibold rounded-lg hover-scale"
                                            style={{ backgroundColor: '#1E88E5', color: '#FFFFFF' }}
                                        >
                                            Copy
                                        </button>
                                    </div>
                                </div>

                                {/* Start Button (Creator Only) */}
                                {isCreator && (
                                    <button
                                        onClick={handleStartBattle}
                                        className="w-full py-3 font-bold text-lg rounded-lg hover-scale"
                                        style={{
                                            background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                            color: '#FFFFFF'
                                        }}
                                    >
                                        🚀 Start Battle
                                    </button>
                                )}
                                {!isCreator && (
                                    <div className="text-center py-3 px-4 rounded-lg" style={{ backgroundColor: '#EFF6FF' }}>
                                        <p className="font-semibold" style={{ color: '#1E40AF' }}>
                                            Waiting for the creator to start the battle...
                                        </p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Participants List */}
                        <div className="bg-white neomorph p-6" style={{ borderRadius: '12px' }}>
                            <h3 className="text-xl font-bold mb-4" style={{ color: '#1A202C' }}>
                                👥 Participants ({participants.length})
                            </h3>
                            <div className="space-y-2">
                                {participants.map((p, index) => (
                                    <div
                                        key={p.user_id}
                                        className="flex items-center gap-3 p-3 rounded-lg"
                                        style={{ backgroundColor: '#F8FAFF' }}
                                    >
                                        <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold"
                                            style={{ backgroundColor: '#1E88E5', color: '#FFFFFF' }}>
                                            {index + 1}
                                        </div>
                                        <p className="font-semibold" style={{ color: '#1A202C' }}>{p.username}</p>
                                        {battleInfo && p.user_id === battleInfo.creator_id && (
                                            <span className="text-xs px-2 py-1 rounded-full font-bold"
                                                style={{ backgroundColor: '#1565C0', color: '#FFFFFF' }}>
                                                CREATOR
                                            </span>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </>
        );
    }

    // Battle In Progress View (NO NAVIGATION during battle)
    if (battleStatus === 'in_progress' && currentQuestion) {
        return (
            <div className="min-h-screen" style={{ backgroundColor: '#F8FAFF', padding: '40px 20px' }}>
                <div className="max-w-6xl mx-auto">
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Main Question Area */}
                        <div className="lg:col-span-2">
                            {/* Timer and Progress */}
                            <div className="bg-white neomorph p-4 mb-6 flex items-center justify-between" style={{ borderRadius: '12px' }}>
                                <div>
                                    <p className="text-sm font-semibold" style={{ color: '#64748B' }}>
                                        Question {questionNumber} of {totalQuestions}
                                    </p>
                                </div>
                                <div className="flex items-center gap-3">
                                    <div className="text-right">
                                        <p className="text-2xl font-black" style={{
                                            color: timeLeft <= Math.min(10, Math.floor(timePerQuestion * 0.16)) ? '#1E40AF' : '#1E88E5'
                                        }}>
                                            {timeLeft}s
                                        </p>
                                    </div>
                                    <div className="w-16 h-16 rounded-full flex items-center justify-center"
                                        style={{
                                            backgroundColor: timeLeft <= Math.min(10, Math.floor(timePerQuestion * 0.16)) ? 'rgba(30, 64, 175, 0.15)' : 'rgba(30, 136, 229, 0.1)',
                                            border: `3px solid ${timeLeft <= Math.min(10, Math.floor(timePerQuestion * 0.16)) ? '#1E40AF' : '#1E88E5'}`
                                        }}>
                                        <span className="text-2xl">⏱️</span>
                                    </div>
                                </div>
                            </div>

                            {/* Question Card */}
                            <div className="bg-white neomorph p-8 mb-6" style={{ borderRadius: '12px' }}>
                                <div className="mb-4">
                                    <span className="px-3 py-1 rounded-full text-sm font-bold"
                                        style={{
                                            backgroundColor: currentQuestion.difficulty === 'Easy' ? 'rgba(59, 130, 246, 0.1)' :
                                                currentQuestion.difficulty === 'Medium' ? 'rgba(30, 64, 175, 0.15)' :
                                                    'rgba(30, 58, 138, 0.2)',
                                            color: currentQuestion.difficulty === 'Easy' ? '#3B82F6' :
                                                currentQuestion.difficulty === 'Medium' ? '#1E40AF' :
                                                    '#1E3A8A'
                                        }}>
                                        {currentQuestion.difficulty}
                                    </span>
                                </div>

                                <h2 className="text-2xl font-bold mb-4" style={{ color: '#1A202C' }}>
                                    {currentQuestion.title}
                                </h2>

                                <p className="text-base leading-relaxed mb-6" style={{ color: '#64748B' }}>
                                    {currentQuestion.description}
                                </p>

                                {/* Options */}
                                <div className="space-y-3">
                                    {['A', 'B', 'C', 'D'].map(option => (
                                        <button
                                            key={option}
                                            onClick={() => !answerResult && setSelectedAnswer(option)}
                                            disabled={answerResult !== null}
                                            className={`w-full text-left p-4 rounded-lg transition ${selectedAnswer === option ? 'hover-lift' : ''
                                                }`}
                                            style={{
                                                border: selectedAnswer === option ? '3px solid #1E88E5' : '2px solid #E2E8F0',
                                                backgroundColor: answerResult ?
                                                    (option === answerResult.correct_answer ? 'rgba(59, 130, 246, 0.15)' :
                                                        option === selectedAnswer && !answerResult.is_correct ? 'rgba(30, 64, 175, 0.1)' :
                                                            '#FFFFFF') :
                                                    (selectedAnswer === option ? 'rgba(30, 136, 229, 0.1)' : '#FFFFFF'),
                                                cursor: answerResult ? 'default' : 'pointer'
                                            }}
                                        >
                                            <span className="font-bold mr-3" style={{ color: '#1E88E5' }}>{option}.</span>
                                            <span style={{ color: '#1A202C' }}>{currentQuestion[`option_${option.toLowerCase()}`]}</span>
                                        </button>
                                    ))}
                                </div>

                                {/* Submit Button */}
                                {!answerResult && (
                                    <button
                                        onClick={handleSubmitAnswer}
                                        disabled={!selectedAnswer}
                                        className="w-full mt-6 py-3 font-bold text-lg rounded-lg hover-scale"
                                        style={{
                                            background: selectedAnswer ? 'linear-gradient(135deg, #1E88E5 0%, #42A5F5 100%)' : '#E2E8F0',
                                            color: selectedAnswer ? '#FFFFFF' : '#64748B',
                                            cursor: selectedAnswer ? 'pointer' : 'not-allowed'
                                        }}
                                    >
                                        Submit Answer
                                    </button>
                                )}

                                {/* Answer Result */}
                                {answerResult && (
                                    <div className={`mt-6 p-4 rounded-lg`}
                                        style={{
                                            backgroundColor: answerResult.is_correct ? 'rgba(59, 130, 246, 0.1)' : 'rgba(30, 64, 175, 0.1)',
                                            border: `2px solid ${answerResult.is_correct ? '#3B82F6' : '#1E40AF'}`
                                        }}>
                                        <p className="font-bold text-lg mb-2" style={{
                                            color: answerResult.is_correct ? '#3B82F6' : '#1E40AF'
                                        }}>
                                            {answerResult.is_correct ? '✓ Correct!' : '✗ Incorrect'}
                                        </p>
                                        <p className="font-semibold mb-2" style={{ color: '#1A202C' }}>
                                            Points Earned: <span style={{ color: '#1E88E5' }}>+{answerResult.points_earned}</span>
                                        </p>
                                        {answerResult.explanation && (
                                            <p className="text-sm" style={{ color: '#64748B' }}>
                                                {answerResult.explanation}
                                            </p>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Leaderboard Sidebar */}
                        <div className="lg:col-span-1">
                            <div className="bg-white neomorph p-6 sticky top-6" style={{ borderRadius: '12px' }}>
                                <h3 className="text-xl font-bold mb-4" style={{ color: '#1A202C' }}>
                                    🏆 Live Leaderboard
                                </h3>
                                <div className="space-y-3">
                                    {leaderboard.map((entry, index) => (
                                        <div
                                            key={entry.user_id}
                                            className="flex items-center gap-3 p-3 rounded-lg"
                                            style={{
                                                backgroundColor: index === 0 ? 'rgba(30, 136, 229, 0.1)' : '#F8FAFF',
                                                border: index === 0 ? '2px solid #1E88E5' : 'none'
                                            }}
                                        >
                                            <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm"
                                                style={{
                                                    background: index === 0 ? 'linear-gradient(135deg, #1565C0, #1E88E5)' :
                                                        index === 1 ? '#64B5F6' :
                                                            index === 2 ? '#90CAF9' : '#E2E8F0',
                                                    color: index < 3 ? '#FFFFFF' : '#64748B'
                                                }}>
                                                {index + 1}
                                            </div>
                                            <div className="flex-1">
                                                <p className="font-semibold text-sm" style={{ color: '#1A202C' }}>
                                                    {entry.username}
                                                </p>
                                                <p className="text-xs" style={{ color: '#64748B' }}>
                                                    {entry.correct_answers} correct
                                                </p>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-bold" style={{ color: '#1E88E5' }}>
                                                    {entry.score}
                                                </p>
                                                <p className="text-xs" style={{ color: '#64748B' }}>
                                                    pts
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // Battle Completed View
    if (battleStatus === 'completed') {
        return (
            <>
                <Navigation />
                <div className="min-h-screen" style={{ backgroundColor: '#F8FAFF', padding: '40px 20px' }}>
                    <div className="max-w-4xl mx-auto">
                        <div className="text-center mb-8">
                            <h1 className="text-5xl font-black mb-4" style={{
                                background: 'linear-gradient(135deg, #1565C0 0%, #1E88E5 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent'
                            }}>
                                🎉 Battle Completed!
                            </h1>
                            <p className="text-lg font-medium" style={{ color: '#64748B' }}>
                                Here are the final results
                            </p>
                        </div>

                        {/* Final Leaderboard */}
                        <div className="bg-white neomorph p-8 mb-6" style={{ borderRadius: '12px' }}>
                            <h2 className="text-2xl font-bold mb-6" style={{ color: '#1A202C' }}>
                                🏆 Final Rankings
                            </h2>
                            <div className="space-y-4">
                                {leaderboard.map((entry, index) => (
                                    <div
                                        key={entry.user_id}
                                        className="flex items-center gap-4 p-4 rounded-lg hover-lift"
                                        style={{
                                            backgroundColor: index === 0 ? 'rgba(30, 136, 229, 0.1)' :
                                                index === 1 ? 'rgba(100, 181, 246, 0.1)' :
                                                    index === 2 ? 'rgba(144, 202, 249, 0.1)' : '#F8FAFF',
                                            border: index < 3 ? `3px solid ${index === 0 ? '#1E88E5' :
                                                index === 1 ? '#64B5F6' : '#90CAF9'
                                                }` : '2px solid #E2E8F0'
                                        }}
                                    >
                                        <div className="w-12 h-12 rounded-full flex items-center justify-center font-bold text-xl"
                                            style={{
                                                background: index === 0 ? 'linear-gradient(135deg, #1565C0, #1E88E5)' :
                                                    index === 1 ? '#64B5F6' :
                                                        index === 2 ? '#90CAF9' : '#E2E8F0',
                                                color: index < 3 ? '#FFFFFF' : '#64748B'
                                            }}>
                                            {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : index + 1}
                                        </div>
                                        <div className="flex-1">
                                            <p className="font-bold text-lg" style={{ color: '#1A202C' }}>
                                                {entry.username}
                                            </p>
                                            <p className="text-sm" style={{ color: '#64748B' }}>
                                                {entry.correct_answers} correct answers • {entry.total_time.toFixed(1)}s total time
                                            </p>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-2xl font-black" style={{ color: '#1E88E5' }}>
                                                {entry.score}
                                            </p>
                                            <p className="text-sm" style={{ color: '#64748B' }}>points</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <button
                            onClick={() => navigate('/dashboard')}
                            className="w-full py-3 font-bold text-lg rounded-lg hover-scale"
                            style={{ backgroundColor: '#1E88E5', color: '#FFFFFF' }}
                        >
                            Back to Dashboard
                        </button>
                    </div>
                </div>
            </>
        );
    }

    return (
        <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#F8FAFF' }}>
            <div className="text-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 mx-auto mb-4"
                    style={{ borderColor: '#1E88E5' }}></div>
                <p className="text-lg font-medium" style={{ color: '#64748B' }}>Loading battle room...</p>
            </div>
        </div>
    );
}

export default BattleRoom;

