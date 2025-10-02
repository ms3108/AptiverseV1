import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import Navigation from './Navigation';

function JoinBattle() {
    const { roomCode } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (roomCode) {
            handleJoinBattle(roomCode);
        }
    }, [roomCode]);

    const handleJoinBattle = async (code) => {
        setLoading(true);
        setError('');

        try {
            const token = localStorage.getItem('token');

            // First, check if battle exists and get info
            const infoResponse = await axios.get(
                `http://localhost:8000/battles/${code}/info`,
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // If battle already started or completed, show error
            if (infoResponse.data.status !== 'waiting') {
                setError('This battle has already started or completed. You cannot join now.');
                setLoading(false);
                return;
            }

            // Join the battle
            await axios.post(
                `http://localhost:8000/battles/${code}/join`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // Navigate to battle room
            navigate(`/battle/${code}`);
        } catch (error) {
            setError(error.response?.data?.detail || 'Failed to join battle room. Please check the room code.');
            setLoading(false);
        }
    };

    return (
        <>
            <Navigation />
            <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: '#F8FAFF', padding: '20px' }}>
                <div className="max-w-md w-full">
                    <div className="bg-white neomorph p-8 text-center" style={{ borderRadius: '12px' }}>
                        {loading && (
                            <>
                                <div className="animate-spin rounded-full h-16 w-16 border-b-4 mx-auto mb-4"
                                    style={{ borderColor: '#1E88E5' }}></div>
                                <p className="text-lg font-semibold" style={{ color: '#1A202C' }}>
                                    Joining battle room...
                                </p>
                                <p className="text-sm mt-2" style={{ color: '#64748B' }}>
                                    Room Code: {roomCode}
                                </p>
                            </>
                        )}

                        {error && (
                            <>
                                <div className="text-6xl mb-4">❌</div>
                                <h2 className="text-2xl font-bold mb-2" style={{ color: '#DC2626' }}>
                                    Failed to Join
                                </h2>
                                <p className="text-sm mb-6" style={{ color: '#64748B' }}>
                                    {error}
                                </p>
                                <button
                                    onClick={() => navigate('/dashboard')}
                                    className="px-6 py-3 font-bold rounded-lg hover-scale"
                                    style={{ backgroundColor: '#1E88E5', color: '#FFFFFF' }}
                                >
                                    Back to Dashboard
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </>
    );
}

export default JoinBattle;
