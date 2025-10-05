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
                <div className="animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#4B0082' }}></div>
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
            <div className="bg-white neomorph p-6" style={{ borderRadius: '12px' }}>
                <h2 className="text-3xl font-semibold mb-2" style={{ color: '#1A202C', letterSpacing: '-0.5px' }}>
                    Welcome back, {stats.username}! 👋
                </h2>
                <p className="text-sm font-medium" style={{ color: '#64748B', letterSpacing: '0.3px' }}>Ready to level up your skills today?</p>
            </div>

            {/* XP and Level Progress - Asymmetrical Design */}
            <div className="relative bg-white neomorph overflow-hidden" style={{ borderRadius: '12px', padding: '32px' }}>
                {/* Diagonal background accent */}
                <div className="absolute top-0 right-0 w-1/3 h-full opacity-5" style={{
                    background: 'linear-gradient(135deg, #4B0082 0%, #39FF14 100%)',
                    clipPath: 'polygon(30% 0, 100% 0, 100% 100%, 0 100%)'
                }}></div>

                <div className="relative z-10">
                    <div className="flex items-start justify-between mb-8">
                        <div className="flex items-center gap-4">
                            {/* Level Badge */}
                            <div className="relative" style={{
                                width: '64px',
                                height: '64px',
                                background: 'linear-gradient(135deg, #4B0082 0%, #6A0DAD 100%)',
                                borderRadius: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                boxShadow: '0 4px 12px rgba(75, 0, 130, 0.3)'
                            }}>
                                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                <div className="absolute -bottom-1 -right-1 bg-white rounded-full px-2 py-0.5 text-xs font-black" style={{ color: '#1E88E5', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
                                    {stats.level}
                                </div>
                            </div>
                            <div>
                                <p className="text-xs font-semibold mb-1" style={{ color: '#64748B', letterSpacing: '0.5px', textTransform: 'uppercase' }}>Current XP</p>
                                <p className="text-4xl font-black" style={{ color: '#1E88E5', fontVariantNumeric: 'tabular-nums', letterSpacing: '-1px' }}>{stats.xp}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-xs font-semibold mb-1" style={{ color: '#64748B', letterSpacing: '0.5px', textTransform: 'uppercase' }}>Next Level</p>
                            <p className="text-4xl font-black" style={{ color: '#1E88E5', fontVariantNumeric: 'tabular-nums', letterSpacing: '-1px' }}>{stats.xp_for_next_level}</p>
                        </div>
                    </div>

                    {/* Enhanced Progress Bar */}
                    <div className="relative w-full rounded-full h-4" style={{ backgroundColor: '#E2E8F0' }}>
                        <div
                            className="rounded-full h-4 transition-all duration-700 ease-out relative overflow-hidden"
                            style={{
                                width: `${Math.min(xpPercentage, 100)}%`,
                                background: 'linear-gradient(90deg, #1E88E5 0%, #42A5F5 50%, #EC4899 100%)',
                                boxShadow: '0 2px 8px rgba(30, 136, 229, 0.4)'
                            }}
                        >
                            {/* Shimmer effect */}
                            <div className="absolute inset-0 opacity-30" style={{
                                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.5), transparent)',
                                animation: 'shimmer 2s infinite'
                            }}></div>
                        </div>
                    </div>
                    <p className="text-xs mt-3 font-semibold" style={{ color: '#64748B', letterSpacing: '0.3px' }}>
                        {stats.xp_progress} / {stats.xp_for_next_level - (stats.level * 100)} XP to reach Level {stats.level + 1}
                    </p>
                </div>
            </div>

            <style>{`
                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
            `}</style>

            {/* Stats Grid - Offset Icon Layout */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Current Streak */}
                <div className="relative bg-white neomorph neomorph-hover hover-lift" style={{ borderRadius: '12px', padding: '32px 24px' }}>
                    {/* Floating icon with pink accent */}
                    <div className="absolute top-4 left-4 flex items-center justify-center" style={{
                        width: '40px',
                        height: '40px',
                        backgroundColor: 'rgba(236, 72, 153, 0.15)',
                        borderRadius: '10px'
                    }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EC4899" strokeWidth="2">
                            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                    <div className="mt-8">
                        <p className="text-xs font-semibold mb-2" style={{ color: '#64748B', letterSpacing: '0.5px', textTransform: 'uppercase' }}>Current Streak</p>
                        <p className="text-4xl font-black mb-1" style={{ color: '#1E88E5', fontVariantNumeric: 'tabular-nums', letterSpacing: '-1px' }}>
                            {stats.current_streak}
                        </p>
                        <p className="text-xs font-medium" style={{ color: '#64748B', letterSpacing: '0.3px' }}>days in a row</p>
                    </div>
                </div>

                {/* Longest Streak - Highlighted */}
                <div className="relative bg-white neomorph neomorph-hover hover-lift" style={{
                    borderRadius: '12px',
                    padding: '32px 24px',
                    border: '2px solid rgba(30, 136, 229, 0.15)',
                    backgroundColor: 'rgba(30, 136, 229, 0.02)'
                }}>
                    {/* Floating icon with pink accent */}
                    <div className="absolute top-4 left-4 flex items-center justify-center" style={{
                        width: '40px',
                        height: '40px',
                        backgroundColor: 'rgba(236, 72, 153, 0.15)',
                        borderRadius: '10px'
                    }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EC4899" strokeWidth="2">
                            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                    {/* "Best" badge */}
                    <div className="absolute top-4 right-4 px-2 py-1 rounded-md text-xs font-bold text-white" style={{
                        background: 'linear-gradient(135deg, #EC4899 0%, #F472B6 100%)'
                    }}>
                        BEST
                    </div>
                    <div className="mt-8">
                        <p className="text-xs font-semibold mb-2" style={{ color: '#64748B', letterSpacing: '0.5px', textTransform: 'uppercase' }}>Longest Streak</p>
                        <p className="text-4xl font-black mb-1" style={{ color: '#1E88E5', fontVariantNumeric: 'tabular-nums', letterSpacing: '-1px' }}>
                            {stats.longest_streak}
                        </p>
                        <p className="text-xs font-medium" style={{ color: '#64748B', letterSpacing: '0.3px' }}>personal best</p>
                    </div>
                </div>

                {/* Total Questions */}
                <div className="relative bg-white neomorph neomorph-hover hover-lift" style={{ borderRadius: '12px', padding: '32px 24px' }}>
                    {/* Floating icon with pink accent */}
                    <div className="absolute top-4 left-4 flex items-center justify-center" style={{
                        width: '40px',
                        height: '40px',
                        backgroundColor: 'rgba(236, 72, 153, 0.15)',
                        borderRadius: '10px'
                    }}>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#EC4899" strokeWidth="2">
                            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" strokeLinecap="round" strokeLinejoin="round" />
                            <polyline points="22 4 12 14.01 9 11.01" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                    <div className="mt-8">
                        <p className="text-xs font-semibold mb-2" style={{ color: '#64748B', letterSpacing: '0.5px', textTransform: 'uppercase' }}>Problems Solved</p>
                        <p className="text-4xl font-black mb-1" style={{ color: '#1E88E5', fontVariantNumeric: 'tabular-nums', letterSpacing: '-1px' }}>
                            {stats.total_questions_solved}
                        </p>
                        <p className="text-xs font-medium" style={{ color: '#64748B', letterSpacing: '0.3px' }}>total questions</p>
                    </div>
                </div>
            </div>

            {/* Badges Section */}
            {stats.badges && stats.badges.length > 0 && (
                <div className="bg-white neomorph p-6" style={{ borderRadius: '12px' }}>
                    <h3 className="text-xl font-bold mb-4" style={{ color: '#212121', letterSpacing: '-0.5px' }}>
                        🏆 Achievements ({stats.badges.length})
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {stats.badges.map((badge, index) => (
                            <div
                                key={index}
                                className="neomorph-hover hover-lift p-4 text-center transition-all border-2"
                                style={{
                                    backgroundColor: 'rgba(236, 72, 153, 0.08)',
                                    borderColor: '#EC4899',
                                    borderRadius: '12px'
                                }}
                                title={badge.description}
                            >
                                <div className="text-4xl mb-2">{badge.icon}</div>
                                <p className="text-sm font-semibold" style={{ color: '#212121' }}>{badge.name}</p>
                                <p className="text-xs mt-1" style={{ color: '#757575' }}>{badge.description}</p>
                                {badge.earned_at && (
                                    <p className="text-xs mt-1" style={{ color: '#757575' }}>
                                        {new Date(badge.earned_at).toLocaleDateString()}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Activity Heatmap */}
            <div className="bg-white neomorph p-6" style={{ borderRadius: '12px' }}>
                <h3 className="text-xl font-bold mb-2" style={{ color: '#212121', letterSpacing: '-0.5px' }}>
                    📊 Activity Heatmap
                </h3>
                <p className="text-sm mb-4 font-medium" style={{ color: '#757575', letterSpacing: '0.3px' }}>
                    Your practice activity over the past 12 weeks
                </p>
                <ActivityHeatmap activityData={stats.activity_data} />
            </div>
        </div>
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

    // Generate 12 weeks of data ending with the current week (Monday start)
    const generateHeatmapData = () => {
        const now = new Date();
        // Force to local timezone to avoid UTC date issues
        const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

        console.log('Heatmap Debug - Today (local):', formatLocalDate(today));
        console.log('Heatmap Debug - Activity Data Keys:', Object.keys(activityData).slice(-10));

        const startOfWeek = new Date(today);
        const dayOfWeek = startOfWeek.getDay();
        const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
        startOfWeek.setDate(startOfWeek.getDate() + diffToMonday);

        const startDate = new Date(startOfWeek);
        startDate.setDate(startDate.getDate() - (7 * 11)); // 11 weeks back so we have 12 including current week

        console.log('Heatmap Debug - Start of Current Week:', formatLocalDate(startOfWeek));
        console.log('Heatmap Debug - Start Date (11 weeks back):', formatLocalDate(startDate));

        const totalDays = 7 * 12;
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

    // Get color intensity based on questions solved - blue to pink gradient
    const getColorStyle = (day) => {
        if (!day) return { backgroundColor: '#E2E8F0' };
        if (day.isFuture) return { backgroundColor: '#E2E8F0', opacity: 0.4 };

        const { questions } = day;
        if (questions === 0) return { backgroundColor: '#E2E8F0' };
        if (questions <= 3) return { backgroundColor: 'rgba(30, 136, 229, 0.3)' }; // Light blue
        if (questions <= 6) return { backgroundColor: 'rgba(30, 136, 229, 0.6)' }; // Medium blue
        if (questions <= 9) return { backgroundColor: 'rgba(236, 72, 153, 0.8)' }; // Light pink
        return { backgroundColor: '#EC4899' }; // Full pink
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
        <div className="overflow-x-auto py-8 px-4">
            <div className="inline-flex flex-col gap-1">
                {/* Month labels */}
                <div className="flex gap-1 mb-2">
                    <div className="w-12"></div>
                    {weeks.map((week, weekIndex) => {
                        const firstDayEntry = week ? week.find(day => day) : null;
                        if (!firstDayEntry) return <div key={weekIndex} style={{ width: '14px' }}></div>;
                        const firstDay = new Date(firstDayEntry.date);
                        const showMonth = weekIndex === 0 || firstDay.getDate() <= 7;
                        return (
                            <div key={weekIndex} className="flex flex-col items-center" style={{ width: '14px' }}>
                                {showMonth && (
                                    <span className="text-xs font-medium mb-1" style={{ color: '#64748B' }}>
                                        {months[firstDay.getMonth()]}
                                    </span>
                                )}
                            </div>
                        );
                    })}
                </div>

                {/* Heatmap grid - rows are days of week, columns are weeks */}
                {[1, 2, 3, 4, 5, 6, 7].map((dayOfWeek) => (
                    <div key={dayOfWeek} className="flex gap-1 items-center">
                        <div className="w-12 text-xs font-medium" style={{ color: '#64748B' }}>
                            {dayLabels[dayOfWeek]}
                        </div>
                        {weeks.map((week, weekIndex) => {
                            const day = week ? week[dayOfWeek - 1] : null;
                            if (!day) return <div key={weekIndex} style={{ width: '14px', height: '14px' }}></div>;

                            // Position tooltip below for top rows (0, 1), above for bottom rows (2, 3, 4)
                            // Also handle left/right edges for better visibility
                            const isTopRow = dayOfWeek <= 3;
                            const isLeftEdge = weekIndex < 2;
                            const isRightEdge = weekIndex >= weeks.length - 2;

                            let tooltipClasses = isTopRow
                                ? "absolute top-full mt-2"
                                : "absolute bottom-full mb-2";

                            // Adjust horizontal positioning for edges
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
                                    className={`transition-all relative group ${day.isFuture ? 'cursor-default' : 'cursor-pointer'}`}
                                    style={{
                                        width: '14px',
                                        height: '14px',
                                        borderRadius: '3px',
                                        ...getColorStyle(day),
                                        transform: 'scale(1)',
                                        boxShadow: day.questions > 0 ? '0 1px 3px rgba(30, 136, 229, 0.2)' : 'none'
                                    }}
                                    onMouseEnter={(e) => {
                                        if (!day.isFuture) {
                                            e.currentTarget.style.transform = 'scale(1.4)';
                                            e.currentTarget.style.zIndex = '10';
                                        }
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.transform = 'scale(1)';
                                        e.currentTarget.style.zIndex = '1';
                                    }}
                                >
                                    {/* Tooltip - position dynamically based on row */}
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
            </div>

            {/* Legend */}
            <div className="flex items-center gap-2 mt-4 text-xs" style={{ color: '#64748B' }}>
                <span>Less</span>
                <div className="flex gap-1">
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#E2E8F0' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: 'rgba(30, 136, 229, 0.3)' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: 'rgba(30, 136, 229, 0.6)' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: 'rgba(236, 72, 153, 0.8)' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#EC4899' }}></div>
                </div>
                <span>More</span>
            </div>
        </div>
    );
}

export default DashboardStats;


