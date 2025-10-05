import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navigation from './Navigation';

function CreateBattle() {
    const navigate = useNavigate();
    const [topics, setTopics] = useState([]);
    const [selectedTopic, setSelectedTopic] = useState('');
    const [numQuestions, setNumQuestions] = useState(5);
    const [timePerQuestion, setTimePerQuestion] = useState(60);  // Default 60 seconds
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchTopics();
    }, []);

    const fetchTopics = async () => {
        try {
            const response = await axios.get('${API_URL}/battles/topics');
            setTopics(response.data.topics);
            if (response.data.topics.length > 0) {
                setSelectedTopic(response.data.topics[0].topic);
            }
        } catch (error) {
            console.error('Failed to fetch topics', error);
        }
    };

    const handleCreateBattle = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const token = localStorage.getItem('token');
            const response = await axios.post(
                '${API_URL}/battles/create',
                {
                    topic: selectedTopic,
                    num_questions: numQuestions,
                    time_per_question: timePerQuestion
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // Join the battle room
            await axios.post(
                `${API_URL}/battles/${response.data.room_code}/join`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // Navigate to battle room
            navigate(`/battle/${response.data.room_code}`);
        } catch (error) {
            setError(error.response?.data?.detail || 'Failed to create battle room');
            setLoading(false);
        }
    };

    const selectedTopicData = topics.find(t => t.topic === selectedTopic);

    return (
        <>
            <Navigation />
            <div className="min-h-screen" style={{ backgroundColor: '#F8FAFF', padding: '40px 20px' }}>
                <div className="max-w-2xl mx-auto">
                    {/* Header */}
                    <div className="text-center mb-8">
                        <h1 className="text-4xl font-black mb-2" style={{
                            background: 'linear-gradient(135deg, #1E88E5 0%, #EC4899 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            letterSpacing: '-1px'
                        }}>
                            ⚔️ Create Battle Room
                        </h1>
                        <p className="text-lg font-medium" style={{ color: '#64748B' }}>
                            Challenge your friends to a real-time quiz battle!
                        </p>
                    </div>

                    {/* Create Battle Form */}
                    <div className="bg-white neomorph p-8" style={{ borderRadius: '12px' }}>
                        <form onSubmit={handleCreateBattle}>
                            {/* Topic Selection */}
                            <div className="mb-6">
                                <label className="block text-sm font-semibold mb-2" style={{ color: '#1A202C' }}>
                                    📚 Select Topic
                                </label>
                                <select
                                    value={selectedTopic}
                                    onChange={(e) => setSelectedTopic(e.target.value)}
                                    className="w-full px-4 py-3 border rounded-lg font-medium"
                                    style={{
                                        backgroundColor: '#F8FAFF',
                                        borderColor: '#E2E8F0',
                                        color: '#1A202C'
                                    }}
                                    required
                                >
                                    {topics.map(topic => (
                                        <option key={topic.topic} value={topic.topic}>
                                            {topic.topic} ({topic.question_count} questions available)
                                        </option>
                                    ))}
                                </select>
                                {selectedTopicData && (
                                    <p className="mt-2 text-sm" style={{ color: '#64748B' }}>
                                        {selectedTopicData.question_count} questions available in this topic
                                    </p>
                                )}
                            </div>

                            {/* Number of Questions */}
                            <div className="mb-6">
                                <label className="block text-sm font-semibold mb-2" style={{ color: '#1A202C' }}>
                                    🎯 Number of Questions
                                </label>
                                <div className="flex items-center gap-4">
                                    <input
                                        type="range"
                                        min="3"
                                        max={selectedTopicData ? Math.min(20, selectedTopicData.question_count) : 20}
                                        value={numQuestions}
                                        onChange={(e) => setNumQuestions(parseInt(e.target.value))}
                                        className="flex-1"
                                        style={{ accentColor: '#1E88E5' }}
                                    />
                                    <div className="w-16 h-16 rounded-full flex items-center justify-center font-black text-xl"
                                        style={{ backgroundColor: 'rgba(30, 136, 229, 0.1)', color: '#1E88E5' }}>
                                        {numQuestions}
                                    </div>
                                </div>
                            </div>

                            {/* Time Per Question */}
                            <div className="mb-6">
                                <label className="block text-sm font-semibold mb-2" style={{ color: '#1A202C' }}>
                                    ⏱️ Time Per Question
                                </label>
                                <div className="flex items-center gap-4">
                                    <input
                                        type="range"
                                        min="10"
                                        max="300"
                                        step="10"
                                        value={timePerQuestion}
                                        onChange={(e) => setTimePerQuestion(parseInt(e.target.value))}
                                        className="flex-1"
                                        style={{ accentColor: '#EC4899' }}
                                    />
                                    <div className="w-16 h-16 rounded-full flex items-center justify-center font-black text-xl"
                                        style={{ backgroundColor: 'rgba(236, 72, 153, 0.1)', color: '#EC4899' }}>
                                        {timePerQuestion}s
                                    </div>
                                </div>
                                <p className="mt-2 text-sm" style={{ color: '#64748B' }}>
                                    Total estimated time: ~{Math.ceil((numQuestions * timePerQuestion) / 60)} minutes
                                </p>
                            </div>

                            {/* Battle Rules */}
                            <div className="mb-6 p-4 rounded-lg" style={{ backgroundColor: '#F8FAFF' }}>
                                <h3 className="font-bold mb-2" style={{ color: '#1A202C' }}>⚡ Battle Rules</h3>
                                <ul className="space-y-1 text-sm" style={{ color: '#64748B' }}>
                                    <li>• All participants receive the same questions simultaneously</li>
                                    <li>• {timePerQuestion} seconds per question</li>
                                    <li>• Correct answer: 100 points + speed bonus (up to 50 points)</li>
                                    <li>• Real-time leaderboard updates</li>
                                    <li>• Winner is determined by highest score</li>
                                </ul>
                            </div>

                            {/* Error Message */}
                            {error && (
                                <div className="mb-4 p-3 rounded-lg" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '2px solid #DC2626' }}>
                                    <p className="text-sm font-semibold" style={{ color: '#DC2626' }}>{error}</p>
                                </div>
                            )}

                            {/* Action Buttons */}
                            <div className="flex gap-3">
                                <button
                                    type="button"
                                    onClick={() => navigate('/dashboard')}
                                    className="flex-1 py-3 font-semibold rounded-lg"
                                    style={{ backgroundColor: '#E2E8F0', color: '#64748B' }}
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={loading || !selectedTopic}
                                    className="flex-1 py-3 font-bold rounded-lg hover-scale"
                                    style={{
                                        background: loading ? '#E2E8F0' : 'linear-gradient(135deg, #EC4899 0%, #F472B6 100%)',
                                        color: loading ? '#64748B' : '#FFFFFF',
                                        cursor: loading ? 'not-allowed' : 'pointer'
                                    }}
                                >
                                    {loading ? 'Creating...' : '🚀 Create Battle Room'}
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Join Existing Battle */}
                    <div className="mt-6 bg-white neomorph p-6 text-center" style={{ borderRadius: '12px' }}>
                        <h3 className="font-bold mb-2" style={{ color: '#1A202C' }}>
                            Have a room code?
                        </h3>
                        <p className="text-sm mb-4" style={{ color: '#64748B' }}>
                            Enter the 6-character room code to join an existing battle
                        </p>
                        <button
                            onClick={() => {
                                const code = prompt('Enter room code:');
                                if (code) {
                                    navigate(`/battle/join/${code.toUpperCase()}`);
                                }
                            }}
                            className="px-6 py-2 font-semibold rounded-lg hover-scale"
                            style={{ backgroundColor: '#1E88E5', color: '#FFFFFF' }}
                        >
                            Join Battle
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}

export default CreateBattle;

