import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';
import axios from 'axios';

function DashboardStats() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchDashboardStats();
    }, []);

    const fetchDashboardStats = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/dashboard/stats`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setStats(response.data);
            setLoading(false);
        } catch (err) {
            setError('Failed to load dashboard stats');
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex justify-center items-center p-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#1E88E5' }}></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-50 border border-red-300 px-4 py-3 rounded-md" style={{ color: '#D32F2F' }}>
                {error}
            </div>
        );
    }

    if (!stats) return null;

    const xpPercentage = (stats.xp_progress / (stats.xp_for_next_level - (stats.level * 100))) * 100;

    return (
        <div className="space-y-6">
            {/* User Header */}
            <div className="relative overflow-hidden bg-white p-8" style={{
                borderRadius: '16px',
                boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)'
            }}>
                <div className="relative z-10">
                    <h2 className="text-2xl font-bold mb-1" style={{ color: '#1F2937' }}>
                        Welcome back, {stats.username}!
                    </h2>
                    <p className="text-sm" style={{ color: '#6B7280' }}>Ready to level up your skills today?</p>
                </div>
            </div>

            {/* XP and Level Progress */}
            <div className="relative overflow-hidden" style={{
                borderRadius: '16px',
                padding: '28px',
                background: 'linear-gradient(135deg, #1E40AF 0%, #3B82F6 100%)',
                boxShadow: '0 4px 20px rgba(59, 130, 246, 0.3)'
            }}>
                <div className="relative z-10">
                    <div className="flex items-start justify-between mb-6">
                        <div className="flex items-center gap-4">
                            {/* Level Badge */}
                            <div className="relative flex items-center justify-center" style={{
                                width: '64px',
                                height: '64px',
                                background: 'rgba(255, 255, 255, 0.2)',
                                borderRadius: '14px',
                                border: '2px solid rgba(255, 255, 255, 0.3)'
                            }}>
                                <span className="text-3xl font-black text-white">{stats.level}</span>
                            </div>
                            <div>
                                <p className="text-xs font-medium mb-1" style={{ color: 'rgba(255,255,255,0.7)' }}>Current XP</p>
                                <p className="text-4xl font-bold text-white">{stats.xp}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-xs font-medium mb-1" style={{ color: 'rgba(255,255,255,0.7)' }}>Next Level</p>
                            <p className="text-4xl font-bold" style={{ color: '#BFDBFE' }}>{stats.xp_for_next_level}</p>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="relative w-full rounded-full h-3" style={{ backgroundColor: 'rgba(255,255,255,0.2)' }}>
                        <div
                            className="rounded-full h-3 transition-all duration-700"
                            style={{
                                width: `${Math.min(xpPercentage, 100)}%`,
                                backgroundColor: '#BFDBFE'
                            }}
                        />
                    </div>
                    <p className="text-sm mt-2" style={{ color: 'rgba(255,255,255,0.8)' }}>
                        {stats.xp_progress} / {stats.xp_for_next_level - (stats.level * 100)} XP to Level {stats.level + 1}
                    </p>
                </div>
            </div>

            {/* Stats Grid - Blue palette */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Current Streak */}
                <div className="bg-white p-6" style={{
                    borderRadius: '16px',
                    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
                    border: '1px solid #E5E7EB'
                }}>
                    <div className="flex items-center gap-3 mb-3">
                        <div className="flex items-center justify-center" style={{
                            width: '40px',
                            height: '40px',
                            backgroundColor: '#EFF6FF',
                            borderRadius: '10px'
                        }}>
                            <span className="text-xl">🔥</span>
                        </div>
                        <p className="text-sm font-medium" style={{ color: '#6B7280' }}>Current Streak</p>
                    </div>
                    <p className="text-3xl font-bold" style={{ color: '#1E40AF' }}>
                        {stats.current_streak}
                    </p>
                    <p className="text-sm" style={{ color: '#6B7280' }}>days</p>
                </div>

                {/* Longest Streak */}
                <div className="bg-white p-6" style={{
                    borderRadius: '16px',
                    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
                    border: '1px solid #E5E7EB'
                }}>
                    <div className="flex items-center gap-3 mb-3">
                        <div className="flex items-center justify-center" style={{
                            width: '40px',
                            height: '40px',
                            backgroundColor: '#EFF6FF',
                            borderRadius: '10px'
                        }}>
                            <span className="text-xl">⚡</span>
                        </div>
                        <p className="text-sm font-medium" style={{ color: '#6B7280' }}>Best Streak</p>
                    </div>
                    <p className="text-3xl font-bold" style={{ color: '#1E40AF' }}>
                        {stats.longest_streak}
                    </p>
                    <p className="text-sm" style={{ color: '#6B7280' }}>personal best</p>
                </div>

                {/* Total Questions */}
                <div className="bg-white p-6" style={{
                    borderRadius: '16px',
                    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)',
                    border: '1px solid #E5E7EB'
                }}>
                    <div className="flex items-center gap-3 mb-3">
                        <div className="flex items-center justify-center" style={{
                            width: '40px',
                            height: '40px',
                            backgroundColor: '#EFF6FF',
                            borderRadius: '10px'
                        }}>
                            <span className="text-xl">✓</span>
                        </div>
                        <p className="text-sm font-medium" style={{ color: '#6B7280' }}>Solved</p>
                    </div>
                    <p className="text-3xl font-bold" style={{ color: '#1E40AF' }}>
                        {stats.total_questions_solved}
                    </p>
                    <p className="text-sm" style={{ color: '#6B7280' }}>questions</p>
                </div>
            </div>

            {/* Badges Section */}
            {stats.badges && stats.badges.length > 0 && (
                <div className="bg-white p-6" style={{
                    borderRadius: '16px',
                    boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)'
                }}>
                    <div className="flex items-center gap-3 mb-5">
                        <div className="flex items-center justify-center" style={{
                            width: '40px',
                            height: '40px',
                            backgroundColor: '#EFF6FF',
                            borderRadius: '10px'
                        }}>
                            <span className="text-xl">🏆</span>
                        </div>
                        <h3 className="text-lg font-semibold" style={{ color: '#1F2937' }}>
                            Achievements ({stats.badges.length})
                        </h3>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {stats.badges.map((badge, index) => (
                            <div
                                key={index}
                                className="p-4 text-center"
                                style={{
                                    backgroundColor: '#F9FAFB',
                                    borderRadius: '12px',
                                    border: '1px solid #E5E7EB'
                                }}
                                title={badge.description}
                            >
                                <div className="text-3xl mb-2">{badge.icon}</div>
                                <p className="text-sm font-semibold" style={{ color: '#1F2937' }}>{badge.name}</p>
                                <p className="text-xs mt-1" style={{ color: '#6B7280' }}>{badge.description}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Activity Heatmap */}
            <div className="bg-white p-6" style={{
                borderRadius: '16px',
                boxShadow: '0 2px 12px rgba(0, 0, 0, 0.06)'
            }}>
                <div className="flex items-center gap-3 mb-2">
                    <div className="flex items-center justify-center" style={{
                        width: '40px',
                        height: '40px',
                        backgroundColor: '#EFF6FF',
                        borderRadius: '10px'
                    }}>
                        <span className="text-xl">📊</span>
                    </div>
                    <h3 className="text-lg font-semibold" style={{ color: '#1F2937' }}>
                        Activity
                    </h3>
                </div>
                <p className="text-sm mb-4" style={{ color: '#6B7280', marginLeft: '52px' }}>
                    Your practice activity over the past 6 months
                </p>
                <ActivityHeatmap activityData={stats.activity_data} />
            </div>
        </div>
        </div >
    );
}

// Activity Heatmap Component
function ActivityHeatmap({ activityData = {} }) {
    // Helper function to format date in local timezone as YYYY-MM-DD
    const formatLocalDate = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    };

    // Generate 26 weeks (6 months) of data ending with the current week (Monday start)
    const generateHeatmapData = () => {
        const now = new Date();
        // Force to local timezone to avoid UTC date issues
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        const startOfWeek = new Date(today);
        const dayOfWeek = startOfWeek.getDay();
        const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
        startOfWeek.setDate(startOfWeek.getDate() + diffToMonday);

        const startDate = new Date(startOfWeek);
        startDate.setDate(startDate.getDate() - (7 * 25)); // 25 weeks back so we have 26 including current week

        const totalDays = 7 * 26;
        const weeks = [];
        let currentWeek = new Array(7).fill(null);

        for (let i = 0; i < totalDays; i++) {
            const currentDate = new Date(startDate);
            currentDate.setDate(startDate.getDate() + i);
            const dateStr = formatLocalDate(currentDate);

            const normalizedDay = currentDate.getDay() === 0 ? 7 : currentDate.getDay();

            if (normalizedDay === 1 && currentWeek.some(cell => cell !== null)) {
                weeks.push(currentWeek);
                currentWeek = new Array(7).fill(null);
            }

            const activity = activityData[dateStr];
            currentWeek[normalizedDay - 1] = {
                date: dateStr,
                dayOfWeek: normalizedDay,
                questions: activity ? activity.questions_solved : 0,
                xp: activity ? activity.xp_earned : 0,
                isFuture: currentDate > today
            };
        }

        weeks.push(currentWeek);
        return weeks;
    };

    const weeks = generateHeatmapData();

    // Get color intensity based on questions solved - blue palette
    const getColorStyle = (day) => {
        if (!day) return { backgroundColor: '#F3F4F6' };
        if (day.isFuture) return { backgroundColor: '#F3F4F6', opacity: 0.4 };

        const { questions } = day;
        if (questions === 0) return { backgroundColor: '#F3F4F6' };
        if (questions <= 3) return { backgroundColor: '#BFDBFE' }; // Light blue
        if (questions <= 6) return { backgroundColor: '#60A5FA' }; // Medium blue
        if (questions <= 9) return { backgroundColor: '#3B82F6' }; // Darker blue
        return { backgroundColor: '#1E40AF' }; // Full dark blue
    };

    const dayLabels = {
        1: 'Mon',
        2: 'Tue',
        3: 'Wed',
        4: 'Thu',
        5: 'Fri',
        6: 'Sat',
        7: 'Sun'
    };
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    return (
        <div className="w-full py-4">
            {/* Month labels */}
            <div
                className="grid gap-[3px] mb-2"
                style={{
                    gridTemplateColumns: `40px repeat(${weeks.length}, 1fr)`,
                }}
            >
                <div></div>
                {weeks.map((week, weekIndex) => {
                    const firstDayEntry = week ? week.find(day => day) : null;
                    if (!firstDayEntry) return <div key={weekIndex}></div>;
                    const firstDay = new Date(firstDayEntry.date);
                    const showMonth = weekIndex === 0 || firstDay.getDate() <= 7;
                    return (
                        <div key={weekIndex} className="text-center">
                            {showMonth && (
                                <span className="text-xs font-medium" style={{ color: '#6B7280' }}>
                                    {months[firstDay.getMonth()]}
                                </span>
                            )}
                        </div>
                    );
                })}
            </div>

            {/* Heatmap grid */}
            {[1, 2, 3, 4, 5, 6, 7].map((dayOfWeek) => (
                <div
                    key={dayOfWeek}
                    className="grid gap-[3px] mb-[3px]"
                    style={{
                        gridTemplateColumns: `40px repeat(${weeks.length}, 1fr)`,
                    }}
                >
                    <div className="text-xs font-medium flex items-center" style={{ color: '#6B7280' }}>
                        {dayLabels[dayOfWeek]}
                    </div>
                    {weeks.map((week, weekIndex) => {
                        const day = week ? week[dayOfWeek - 1] : null;
                        if (!day) return <div key={weekIndex} className="aspect-square rounded-sm" style={{ backgroundColor: '#F3F4F6' }}></div>;

                        const isTopRow = dayOfWeek <= 3;
                        const isLeftEdge = weekIndex < 2;
                        const isRightEdge = weekIndex >= weeks.length - 2;

                        let tooltipClasses = isTopRow
                            ? "absolute top-full mt-2"
                            : "absolute bottom-full mb-2";

                        if (isLeftEdge) {
                            tooltipClasses += " left-0";
                        } else if (isRightEdge) {
                            tooltipClasses += " right-0";
                        } else {
                            tooltipClasses += " left-1/2 transform -translate-x-1/2";
                        }

                        return (
                            <div
                                key={weekIndex}
                                className={`aspect-square transition-all relative group ${day.isFuture ? 'cursor-default' : 'cursor-pointer'}`}
                                style={{
                                    borderRadius: '3px',
                                    ...getColorStyle(day),
                                    boxShadow: day.questions > 0 ? '0 1px 3px rgba(59, 130, 246, 0.3)' : 'none'
                                }}
                                onMouseEnter={(e) => {
                                    if (!day.isFuture) {
                                        e.currentTarget.style.transform = 'scale(1.2)';
                                        e.currentTarget.style.zIndex = '10';
                                    }
                                }}
                                onMouseLeave={(e) => {
                                    e.currentTarget.style.transform = 'scale(1)';
                                    e.currentTarget.style.zIndex = '1';
                                }}
                            >
                                <div className={`${tooltipClasses} px-3 py-2 text-xs font-medium text-white rounded-lg opacity-0 ${day.isFuture ? '' : 'group-hover:opacity-100'} transition-opacity pointer-events-none whitespace-nowrap`}
                                    style={{
                                        backgroundColor: '#1F2937',
                                        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                                        zIndex: '50'
                                    }}>
                                    <div className="font-semibold mb-1">{new Date(day.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}</div>
                                    {day.isFuture ? (
                                        <div style={{ color: '#94A3B8' }}>Upcoming</div>
                                    ) : (
                                        <>
                                            <div style={{ color: '#60A5FA' }}>{day.questions} question{day.questions !== 1 ? 's' : ''}</div>
                                            <div style={{ color: '#F472B6' }}>{day.xp} XP</div>
                                        </>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            ))}

            {/* Legend */}
            <div className="flex items-center justify-end gap-2 mt-4 text-xs" style={{ color: '#6B7280' }}>
                <span>Less</span>
                <div className="flex gap-1">
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#F3F4F6' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#BBF7D0' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#4ADE80' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#16A34A' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#15803D' }}></div>
                </div>
                <span>More</span>
            </div>
        </div>
    );
}

export default DashboardStats;


