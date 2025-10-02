import React, { useState, useEffect } from 'react';
import axios from 'axios';

function DiscussionSection({ questionId, isSolved }) {
    const [discussions, setDiscussions] = useState([]);
    const [newDiscussion, setNewDiscussion] = useState('');
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');
    const [reportModal, setReportModal] = useState({ isOpen: false, discussionId: null, username: '' });
    const [reportReason, setReportReason] = useState('');
    const [reportSubmitting, setReportSubmitting] = useState(false);

    useEffect(() => {
        if (isSolved) {
            fetchDiscussions();
        }
    }, [questionId, isSolved]);

    const fetchDiscussions = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(
                `http://localhost:8000/discussions/${questionId}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setDiscussions(response.data.discussions);
            setLoading(false);
        } catch (err) {
            console.error('Failed to load discussions', err);
            setLoading(false);
        }
    };

    const handleSubmitDiscussion = async (e) => {
        e.preventDefault();

        if (newDiscussion.trim().length < 10) {
            setError('Discussion must be at least 10 characters long');
            return;
        }

        setSubmitting(true);
        setError('');

        try {
            const token = localStorage.getItem('token');
            const response = await axios.post(
                'http://localhost:8000/discussions',
                {
                    question_id: questionId,
                    content: newDiscussion.trim()
                },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            setDiscussions([response.data, ...discussions]);
            setNewDiscussion('');
            setSubmitting(false);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to post discussion');
            setSubmitting(false);
        }
    };

    const handleVote = async (discussionId, voteType) => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.post(
                `http://localhost:8000/discussions/${discussionId}/vote?vote_type=${voteType}`,
                {},
                { headers: { Authorization: `Bearer ${token}` } }
            );

            // Update the discussion in the list
            setDiscussions(discussions.map(d =>
                d.id === discussionId
                    ? {
                        ...d,
                        upvotes: response.data.upvotes,
                        downvotes: response.data.downvotes,
                        user_vote: response.data.user_vote
                    }
                    : d
            ).sort((a, b) => (b.upvotes - b.downvotes) - (a.upvotes - a.downvotes) || new Date(b.created_at) - new Date(a.created_at)));
        } catch (err) {
            console.error('Failed to vote', err);
        }
    };

    const handleDelete = async (discussionId) => {
        if (!window.confirm('Are you sure you want to delete this discussion?')) {
            return;
        }

        try {
            const token = localStorage.getItem('token');
            await axios.delete(
                `http://localhost:8000/discussions/${discussionId}`,
                { headers: { Authorization: `Bearer ${token}` } }
            );

            setDiscussions(discussions.filter(d => d.id !== discussionId));
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to delete discussion');
        }
    };

    const handleReport = async () => {
        if (!reportReason.trim()) {
            alert('Please provide a reason for reporting');
            return;
        }

        setReportSubmitting(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(
                `http://localhost:8000/discussions/${reportModal.discussionId}/report`,
                { reason: reportReason.trim() },
                { headers: { Authorization: `Bearer ${token}` } }
            );

            alert('Post reported successfully. Our team will review it shortly.');
            setReportModal({ isOpen: false, discussionId: null, username: '' });
            setReportReason('');
        } catch (err) {
            alert(err.response?.data?.detail || 'Failed to report post');
        } finally {
            setReportSubmitting(false);
        }
    };

    if (!isSolved) {
        return (
            <div className="bg-blue-50 border-2 p-6 text-center neomorph" style={{ borderColor: '#1E88E5', borderRadius: '12px' }}>
                <p className="text-base font-semibold" style={{ color: '#1E88E5', letterSpacing: '0.3px' }}>
                    💡 Solve this question to unlock the community discussion area!
                </p>
            </div>
        );
    }

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    };

    return (
        <div className="bg-white neomorph p-6 mt-6" style={{ borderRadius: '12px' }}>
            <h3 className="text-2xl font-bold mb-2" style={{ color: '#212121', letterSpacing: '-0.5px' }}>
                💬 Community Discussion
            </h3>
            <p className="text-sm mb-6 font-medium" style={{ color: '#757575', letterSpacing: '0.3px' }}>
                Share your approach, ask questions, or discuss alternative solutions
            </p>

            {/* New Discussion Form */}
            <form onSubmit={handleSubmitDiscussion} className="mb-6">
                <textarea
                    value={newDiscussion}
                    onChange={(e) => setNewDiscussion(e.target.value)}
                    placeholder="Share your solution method, tips, or ask a question... (minimum 10 characters)"
                    className="w-full px-4 py-3 border resize-none transition focus:outline-none focus:ring-2"
                    style={{
                        backgroundColor: '#FAFAFA',
                        borderColor: '#E0E0E0',
                        color: '#212121',
                        borderRadius: '10px',
                        boxShadow: '0px 2px 6px rgba(0, 0, 0, 0.04)'
                    }}
                    rows="4"
                    maxLength="5000"
                />
                {error && (
                    <p className="text-sm mt-2 font-medium" style={{ color: '#D32F2F' }}>{error}</p>
                )}
                <div className="flex items-center justify-between mt-3">
                    <span className="text-xs" style={{ color: '#757575' }}>
                        {newDiscussion.length}/5000 characters
                    </span>
                    <button
                        type="submit"
                        disabled={submitting || newDiscussion.trim().length < 10}
                        className="px-6 py-2 font-semibold transition hover-scale"
                        style={{
                            backgroundColor: submitting || newDiscussion.trim().length < 10 ? '#E0E0E0' : '#1E88E5',
                            color: submitting || newDiscussion.trim().length < 10 ? '#64748B' : '#FFFFFF',
                            cursor: submitting || newDiscussion.trim().length < 10 ? 'not-allowed' : 'pointer',
                            borderRadius: '10px',
                            boxShadow: submitting || newDiscussion.trim().length < 10 ? 'none' : '0px 4px 10px rgba(30, 136, 229, 0.25)'
                        }}
                    >
                        {submitting ? 'Posting...' : 'Post Discussion'}
                    </button>
                </div>
            </form>

            {/* Discussions List */}
            {loading ? (
                <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto" style={{ borderColor: '#1E88E5' }}></div>
                </div>
            ) : discussions.length === 0 ? (
                <div className="text-center py-8 neomorph" style={{ backgroundColor: '#FAFAFA', borderRadius: '12px' }}>
                    <p className="font-medium" style={{ color: '#757575', letterSpacing: '0.3px' }}>No discussions yet. Be the first to share your thoughts!</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {discussions.map((discussion) => (
                        <div
                            key={discussion.id}
                            className="neomorph neomorph-hover hover-lift p-4"
                            style={{
                                backgroundColor: '#FAFAFA',
                                borderRadius: '12px'
                            }}
                        >
                            <div className="flex items-start gap-4">
                                {/* Vote Section */}
                                <div className="flex flex-col items-center gap-1">
                                    <button
                                        onClick={() => handleVote(discussion.id, 1)}
                                        className="p-2 transition hover-scale"
                                        style={{
                                            backgroundColor: discussion.user_vote === 1 ? '#1E88E5' : '#E0E0E0',
                                            color: discussion.user_vote === 1 ? '#FFFFFF' : '#64748B',
                                            borderRadius: '8px',
                                            boxShadow: discussion.user_vote === 1 ? '0 2px 8px rgba(30, 136, 229, 0.3)' : 'none'
                                        }}
                                        title={discussion.user_vote === 1 ? 'Remove upvote' : 'Upvote'}
                                    >
                                        <svg
                                            className="w-4 h-4"
                                            fill={discussion.user_vote === 1 ? 'currentColor' : 'none'}
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M5 15l7-7 7 7"
                                            />
                                        </svg>
                                    </button>
                                    <span className="text-sm font-bold" style={{ color: '#1E88E5' }}>
                                        {discussion.upvotes - discussion.downvotes}
                                    </span>
                                    <button
                                        onClick={() => handleVote(discussion.id, -1)}
                                        className="p-2 transition hover-scale"
                                        style={{
                                            backgroundColor: discussion.user_vote === -1 ? '#D32F2F' : '#E0E0E0',
                                            color: discussion.user_vote === -1 ? '#FFFFFF' : '#64748B',
                                            borderRadius: '8px',
                                            boxShadow: discussion.user_vote === -1 ? '0 2px 8px rgba(211, 47, 47, 0.3)' : 'none'
                                        }}
                                        title={discussion.user_vote === -1 ? 'Remove downvote' : 'Downvote'}
                                    >
                                        <svg
                                            className="w-4 h-4"
                                            fill={discussion.user_vote === -1 ? 'currentColor' : 'none'}
                                            stroke="currentColor"
                                            viewBox="0 0 24 24"
                                        >
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M19 9l-7 7-7-7"
                                            />
                                        </svg>
                                    </button>
                                </div>

                                {/* Discussion Content */}
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            <span className="font-semibold" style={{ color: '#1E88E5' }}>
                                                {discussion.username}
                                            </span>
                                            <span className="text-xs" style={{ color: '#757575' }}>
                                                {formatDate(discussion.created_at)}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            {discussion.user_id === JSON.parse(localStorage.getItem('user'))?.id ? (
                                                <button
                                                    onClick={() => handleDelete(discussion.id)}
                                                    className="text-xs font-semibold transition hover:opacity-80"
                                                    style={{ color: '#D32F2F' }}
                                                >
                                                    Delete
                                                </button>
                                            ) : (
                                                <button
                                                    onClick={() => setReportModal({
                                                        isOpen: true,
                                                        discussionId: discussion.id,
                                                        username: discussion.username
                                                    })}
                                                    className="text-xs font-semibold transition hover:opacity-80 flex items-center gap-1"
                                                    style={{ color: '#FF6B6B' }}
                                                    title="Report this post"
                                                >
                                                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
                                                    </svg>
                                                    Report
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                    <p className="text-sm whitespace-pre-wrap leading-relaxed" style={{ color: '#212121' }}>
                                        {discussion.content}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Report Modal */}
            {reportModal.isOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
                    onClick={() => {
                        setReportModal({ isOpen: false, discussionId: null, username: '' });
                        setReportReason('');
                    }}
                >
                    <div
                        className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div>
                                <h3 className="text-xl font-bold" style={{ color: '#212121' }}>
                                    🚩 Report Post
                                </h3>
                                <p className="text-sm mt-1" style={{ color: '#757575' }}>
                                    Report post by <span className="font-semibold">{reportModal.username}</span>
                                </p>
                            </div>
                            <button
                                onClick={() => {
                                    setReportModal({ isOpen: false, discussionId: null, username: '' });
                                    setReportReason('');
                                }}
                                className="text-gray-400 hover:text-gray-600 transition"
                            >
                                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                </svg>
                            </button>
                        </div>

                        <div className="mb-4">
                            <label className="block text-sm font-medium mb-2" style={{ color: '#212121' }}>
                                Reason for reporting *
                            </label>
                            <textarea
                                value={reportReason}
                                onChange={(e) => setReportReason(e.target.value)}
                                placeholder="Please describe why this post violates community guidelines..."
                                className="w-full px-4 py-3 border resize-none transition focus:outline-none focus:ring-2"
                                style={{
                                    backgroundColor: '#FAFAFA',
                                    borderColor: '#E0E0E0',
                                    color: '#212121',
                                    borderRadius: '10px',
                                    boxShadow: '0px 2px 6px rgba(0, 0, 0, 0.04)'
                                }}
                                rows="4"
                                maxLength="500"
                            />
                            <p className="text-xs mt-1" style={{ color: '#757575' }}>
                                {reportReason.length}/500 characters
                            </p>
                        </div>

                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
                            <p className="text-xs" style={{ color: '#B45309' }}>
                                ⚠️ False reports may result in action against your account. Please only report content that violates our community guidelines.
                            </p>
                        </div>

                        <div className="flex gap-3">
                            <button
                                onClick={() => {
                                    setReportModal({ isOpen: false, discussionId: null, username: '' });
                                    setReportReason('');
                                }}
                                className="flex-1 px-4 py-2 font-semibold transition hover:opacity-80"
                                style={{
                                    backgroundColor: '#E0E0E0',
                                    color: '#64748B',
                                    borderRadius: '10px'
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleReport}
                                disabled={reportSubmitting || !reportReason.trim()}
                                className="flex-1 px-4 py-2 font-semibold transition hover:opacity-90"
                                style={{
                                    backgroundColor: reportSubmitting || !reportReason.trim() ? '#E0E0E0' : '#FF6B6B',
                                    color: reportSubmitting || !reportReason.trim() ? '#64748B' : '#FFFFFF',
                                    cursor: reportSubmitting || !reportReason.trim() ? 'not-allowed' : 'pointer',
                                    borderRadius: '10px',
                                    boxShadow: reportSubmitting || !reportReason.trim() ? 'none' : '0px 4px 10px rgba(255, 107, 107, 0.25)'
                                }}
                            >
                                {reportSubmitting ? 'Submitting...' : 'Submit Report'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default DiscussionSection;
