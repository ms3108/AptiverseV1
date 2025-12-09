import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navigation from './Navigation';

function BattleHistory() {
    const navigate = useNavigate();
    const [battles, setBattles] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState('all'); // all, completed, in_progress

    useEffect(() => {
        fetchBattleHistory();
    }, []);

    const fetchBattleHistory = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/battles/history`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setBattles(response.data.battles);
            setLoading(false);
        } catch (error) {
            console.error('Failed to fetch battle history', error);
            setLoading(false);
        }
    };

    const filteredBattles = battles.filter(battle => {
        if (filter === 'all') return true;
        if (filter === 'completed') return battle.status === 'completed';
        if (filter === 'in_progress') return battle.status === 'in_progress';
        return true;
    });

    const getRankMedal = (rank) => {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return `#${rank}`;
    };

    const getRankColor = (rank) => {
        if (rank === 1) return '#1E88E5';
        if (rank === 2) return '#64B5F6';
        if (rank === 3) return '#90CAF9';
        return '#64748B';
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#F8FAFF' }}>
                <div className="text-center">
                    <div className="animate-spin rounded-full h-16 w-16 border-b-4 mx-auto mb-4"
                        style={{ borderColor: '#1E88E5' }}></div>
                    <p className="text-lg font-medium" style={{ color: '#64748B' }}>Loading battle history...</p>
                </div>
            </div>
        );
    }

    return (
        <>
            <Navigation />
            <div className="min-h-screen" style={{ backgroundColor: '#F8FAFF', padding: '40px 20px' }}>
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <div className="mb-8">
                        <div className="flex items-center justify-between mb-4">
                            <h1 className="text-4xl font-black" style={{
                                background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                letterSpacing: '-1px'
                            }}>
                                ⚔️ Battle History
                            </h1>
                            <button
                                onClick={() => navigate('/battle/create')}
                                className="px-6 py-3 font-bold rounded-lg hover-scale"
                                style={{
                                    background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                    color: '#FFFFFF'
                                }}
                            >
                                + New Battle
                            </button>
                        </div>

                        {/* Filters */}
                        <div className="flex gap-3">
                            {['all', 'completed', 'in_progress'].map(f => (
                                <button
                                    key={f}
                                    onClick={() => setFilter(f)}
                                    className="px-4 py-2 font-semibold rounded-lg transition"
                                    style={{
                                        backgroundColor: filter === f ? '#1E88E5' : '#FFFFFF',
                                        color: filter === f ? '#FFFFFF' : '#64748B',
                                        border: filter === f ? 'none' : '2px solid #E2E8F0'
                                    }}
                                >
                                    {f.charAt(0).toUpperCase() + f.slice(1).replace('_', ' ')}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Battles List */}
                    {filteredBattles.length === 0 ? (
                        <div className="bg-white neomorph p-12 text-center" style={{ borderRadius: '12px' }}>
                            <div className="text-6xl mb-4">🎮</div>
                            <h3 className="text-2xl font-bold mb-2" style={{ color: '#1A202C' }}>
                                No battles yet
                            </h3>
                            <p className="text-base mb-6" style={{ color: '#64748B' }}>
                                Create your first battle and challenge your friends!
                            </p>
                            <button
                                onClick={() => navigate('/battle/create')}
                                className="px-8 py-3 font-bold rounded-lg hover-scale"
                                style={{ backgroundColor: '#1E88E5', color: '#FFFFFF' }}
                            >
                                Create Battle
                            </button>
                        </div>
                    ) : (
                        <div className="grid gap-4">
                            {filteredBattles.map(battle => (
                                <div
                                    key={battle.battle_id}
                                    className="bg-white neomorph neomorph-hover hover-lift p-6"
                                    style={{ borderRadius: '12px' }}
                                >
                                    <div className="flex items-start gap-6">
                                        {/* Rank Badge */}
                                        {battle.status === 'completed' && battle.rank && (
                                            <div className="flex-shrink-0">
                                                <div
                                                    className="w-16 h-16 rounded-full flex items-center justify-center font-black text-2xl"
                                                    style={{
                                                        backgroundColor: `${getRankColor(battle.rank)}20`,
                                                        border: `3px solid ${getRankColor(battle.rank)}`,
                                                        color: getRankColor(battle.rank)
                                                    }}
                                                >
                                                    {getRankMedal(battle.rank)}
                                                </div>
                                            </div>
                                        )}

                                        {/* Battle Info */}
                                        <div className="flex-1">
                                            <div className="flex items-start justify-between mb-3">
                                                <div>
                                                    <h3 className="text-xl font-bold mb-1" style={{ color: '#1A202C' }}>
                                                        {battle.topic}
                                                    </h3>
                                                    <div className="flex items-center gap-3 text-sm">
                                                        <span className="font-semibold" style={{ color: '#64748B' }}>
                                                            Room: <span style={{ color: '#1E88E5' }}>{battle.room_code}</span>
                                                        </span>
                                                        <span>•</span>
                                                        <span style={{ color: '#64748B' }}>
                                                            {battle.num_questions} questions
                                                        </span>
                                                        <span>•</span>
                                                        <span style={{ color: '#64748B' }}>
                                                            {battle.total_participants} participants
                                                        </span>
                                                    </div>
                                                </div>

                                                {/* Status Badge */}
                                                <span
                                                    className="px-3 py-1 rounded-full text-xs font-bold"
                                                    style={{
                                                        backgroundColor: battle.status === 'completed' ? 'rgba(30, 64, 175, 0.1)' :
                                                            battle.status === 'in_progress' ? 'rgba(59, 130, 246, 0.1)' :
                                                                'rgba(100, 116, 139, 0.1)',
                                                        color: battle.status === 'completed' ? '#1E40AF' :
                                                            battle.status === 'in_progress' ? '#3B82F6' :
                                                                '#64748B'
                                                    }}
                                                >
                                                    {battle.status === 'completed' ? '✓ Completed' :
                                                        battle.status === 'in_progress' ? '⚡ In Progress' :
                                                            '⏸️ Waiting'}
                                                </span>
                                            </div>

                                            {/* Stats */}
                                            {battle.status === 'completed' && (
                                                <div className="grid grid-cols-4 gap-4 p-4 rounded-lg"
                                                    style={{ backgroundColor: '#F8FAFF' }}>
                                                    <div>
                                                        <p className="text-xs font-semibold mb-1" style={{ color: '#64748B' }}>
                                                            FINAL RANK
                                                        </p>
                                                        <p className="text-2xl font-black" style={{ color: getRankColor(battle.rank) }}>
                                                            {battle.rank}/{battle.total_participants}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs font-semibold mb-1" style={{ color: '#64748B' }}>
                                                            SCORE
                                                        </p>
                                                        <p className="text-2xl font-black" style={{ color: '#1E88E5' }}>
                                                            {battle.score}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs font-semibold mb-1" style={{ color: '#64748B' }}>
                                                            CORRECT
                                                        </p>
                                                        <p className="text-2xl font-black" style={{ color: '#3B82F6' }}>
                                                            {battle.correct_answers}/{battle.num_questions}
                                                        </p>
                                                    </div>
                                                    <div>
                                                        <p className="text-xs font-semibold mb-1" style={{ color: '#64748B' }}>
                                                            ACCURACY
                                                        </p>
                                                        <p className="text-2xl font-black" style={{ color: '#1565C0' }}>
                                                            {((battle.correct_answers / battle.num_questions) * 100).toFixed(0)}%
                                                        </p>
                                                    </div>
                                                </div>
                                            )}

                                            {/* Date */}
                                            <p className="text-xs mt-3" style={{ color: '#64748B' }}>
                                                {battle.completed_at ?
                                                    `Completed: ${formatDate(battle.completed_at)}` :
                                                    `Created: ${formatDate(battle.created_at)}`
                                                }
                                            </p>
                                        </div>

                                        {/* Action Button */}
                                        {battle.status === 'in_progress' && (
                                            <button
                                                onClick={() => navigate(`/battle/${battle.room_code}`)}
                                                className="flex-shrink-0 px-6 py-3 font-bold rounded-lg hover-scale"
                                                style={{ backgroundColor: '#1E88E5', color: '#FFFFFF' }}
                                            >
                                                Rejoin
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div >
        </>
    );
}

export default BattleHistory;


