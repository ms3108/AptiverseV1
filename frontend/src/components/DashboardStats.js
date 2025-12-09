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
            {/* User Header - with gradient accent */}
            <div className="relative overflow-hidden bg-white p-8" style={{
                borderRadius: '20px',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)'
            }}>
                <div className="absolute top-0 right-0 w-64 h-64 opacity-10" style={{
                    background: 'radial-gradient(circle, #6366F1 0%, transparent 70%)',
                    transform: 'translate(30%, -30%)'
                }}></div>
                <div className="relative z-10">
                    <h2 className="text-3xl font-bold mb-2" style={{ color: '#1F2937', letterSpacing: '-0.5px' }}>
                        Welcome back, {stats.username}! <span className="inline-block animate-bounce">👋</span>
                    </h2>
                    <p className="text-base" style={{ color: '#6B7280' }}>Ready to level up your skills today?</p>
                </div>
            </div>

            {/* XP and Level Progress - Premium Card */}
            <div className="relative overflow-hidden" style={{
                borderRadius: '20px',
                padding: '32px',
                background: 'linear-gradient(135deg, #1E3A5F 0%, #2D5A87 50%, #3B7CB8 100%)',
                boxShadow: '0 10px 40px rgba(30, 58, 95, 0.3)'
            }}>
                {/* Decorative elements */}
                <div className="absolute top-0 right-0 w-40 h-40 opacity-20" style={{
                    background: 'radial-gradient(circle, #60A5FA 0%, transparent 70%)',
                }}></div>
                <div className="absolute bottom-0 left-0 w-32 h-32 opacity-10" style={{
                    background: 'radial-gradient(circle, #F59E0B 0%, transparent 70%)',
                }}></div>

                <div className="relative z-10">
                    <div className="flex items-start justify-between mb-8">
                        <div className="flex items-center gap-5">
                            {/* Level Badge - Golden accent */}
                            <div className="relative" style={{
                                width: '72px',
                                height: '72px',
                                background: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
                                borderRadius: '16px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                boxShadow: '0 8px 24px rgba(245, 158, 11, 0.4)'
                            }}>
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2.5">
                                    <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                <div className="absolute -bottom-2 -right-2 bg-white rounded-full px-3 py-1 text-sm font-black" style={{
                                    color: '#D97706',
                                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
                                }}>
                                    {stats.level}
                                </div>
                            </div>
                            <div>
                                <p className="text-xs font-semibold mb-1 tracking-wider" style={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase' }}>Current XP</p>
                                <p className="text-5xl font-black" style={{ color: 'white', fontVariantNumeric: 'tabular-nums', letterSpacing: '-2px' }}>{stats.xp}</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <p className="text-xs font-semibold mb-1 tracking-wider" style={{ color: 'rgba(255,255,255,0.7)', textTransform: 'uppercase' }}>Next Level</p>
                            <p className="text-5xl font-black" style={{ color: '#60A5FA', fontVariantNumeric: 'tabular-nums', letterSpacing: '-2px' }}>{stats.xp_for_next_level}</p>
                        </div>
                    </div>

                    {/* Enhanced Progress Bar */}
                    <div className="relative w-full rounded-full h-4" style={{ backgroundColor: 'rgba(255,255,255,0.2)' }}>
                        <div
                            className="rounded-full h-4 transition-all duration-700 ease-out relative overflow-hidden"
                            style={{
                                width: `${Math.min(xpPercentage, 100)}%`,
                                background: 'linear-gradient(90deg, #34D399 0%, #10B981 50%, #059669 100%)',
                                boxShadow: '0 0 20px rgba(52, 211, 153, 0.5)'
                            }}
                        >
                            <div className="absolute inset-0 opacity-40" style={{
                                background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent)',
                                animation: 'shimmer 2s infinite'
                            }}></div>
                        </div>
                    </div>
                    <p className="text-sm mt-3 font-medium" style={{ color: 'rgba(255,255,255,0.8)' }}>
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

            {/* Stats Grid - Colorful Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                {/* Current Streak - Orange/Amber theme */}
                <div className="relative overflow-hidden bg-white hover-lift" style={{
                    borderRadius: '20px',
                    padding: '28px',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
                    border: '1px solid #FEF3C7',
                    transition: 'all 0.3s ease'
                }}>
                    <div className="absolute top-0 right-0 w-24 h-24 opacity-20" style={{
                        background: 'radial-gradient(circle, #F59E0B 0%, transparent 70%)',
                    }}></div>
                    <div className="flex items-center justify-center mb-4" style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)',
                        borderRadius: '12px'
                    }}>
                        <span className="text-2xl">🔥</span>
                    </div>
                    <p className="text-xs font-semibold mb-2 tracking-wider" style={{ color: '#92400E', textTransform: 'uppercase' }}>Current Streak</p>
                    <p className="text-4xl font-black mb-1" style={{ color: '#D97706', fontVariantNumeric: 'tabular-nums' }}>
                        {stats.current_streak}
                    </p>
                    <p className="text-sm font-medium" style={{ color: '#B45309' }}>days in a row</p>
                </div>

                {/* Longest Streak - Purple theme */}
                <div className="relative overflow-hidden bg-white hover-lift" style={{
                    borderRadius: '20px',
                    padding: '28px',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
                    border: '1px solid #EDE9FE',
                    transition: 'all 0.3s ease'
                }}>
                    <div className="absolute top-0 right-0 w-24 h-24 opacity-20" style={{
                        background: 'radial-gradient(circle, #8B5CF6 0%, transparent 70%)',
                    }}></div>
                    {/* "Best" badge */}
                    <div className="absolute top-4 right-4 px-3 py-1 rounded-full text-xs font-bold text-white" style={{
                        background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)'
                    }}>
                        ⭐ BEST
                    </div>
                    <div className="flex items-center justify-center mb-4" style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #EDE9FE 0%, #DDD6FE 100%)',
                        borderRadius: '12px'
                    }}>
                        <span className="text-2xl">⚡</span>
                    </div>
                    <p className="text-xs font-semibold mb-2 tracking-wider" style={{ color: '#5B21B6', textTransform: 'uppercase' }}>Longest Streak</p>
                    <p className="text-4xl font-black mb-1" style={{ color: '#7C3AED', fontVariantNumeric: 'tabular-nums' }}>
                        {stats.longest_streak}
                    </p>
                    <p className="text-sm font-medium" style={{ color: '#6D28D9' }}>personal best</p>
                </div>

                {/* Total Questions - Green theme */}
                <div className="relative overflow-hidden bg-white hover-lift" style={{
                    borderRadius: '20px',
                    padding: '28px',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)',
                    border: '1px solid #D1FAE5',
                    transition: 'all 0.3s ease'
                }}>
                    <div className="absolute top-0 right-0 w-24 h-24 opacity-20" style={{
                        background: 'radial-gradient(circle, #10B981 0%, transparent 70%)',
                    }}></div>
                    <div className="flex items-center justify-center mb-4" style={{
                        width: '48px',
                        height: '48px',
                        background: 'linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%)',
                        borderRadius: '12px'
                    }}>
                        <span className="text-2xl">✅</span>
                    </div>
                    <p className="text-xs font-semibold mb-2 tracking-wider" style={{ color: '#047857', textTransform: 'uppercase' }}>Problems Solved</p>
                    <p className="text-4xl font-black mb-1" style={{ color: '#059669', fontVariantNumeric: 'tabular-nums' }}>
                        {stats.total_questions_solved}
                    </p>
                    <p className="text-sm font-medium" style={{ color: '#047857' }}>total questions</p>
                </div>
            </div>

            {/* Badges Section - Redesigned */}
            {stats.badges && stats.badges.length > 0 && (
                <div className="bg-white p-8" style={{
                    borderRadius: '20px',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)'
                }}>
                    <div className="flex items-center gap-3 mb-6">
                        <div className="flex items-center justify-center" style={{
                            width: '40px',
                            height: '40px',
                            background: 'linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%)',
                            borderRadius: '10px'
                        }}>
                            <span className="text-xl">🏆</span>
                        </div>
                        <h3 className="text-xl font-bold" style={{ color: '#1F2937' }}>
                            Achievements <span className="text-base font-normal" style={{ color: '#6B7280' }}>({stats.badges.length})</span>
                        </h3>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        {stats.badges.map((badge, index) => (
                            <div
                                key={index}
                                className="hover-lift p-5 text-center transition-all"
                                style={{
                                    background: 'linear-gradient(135deg, #F9FAFB 0%, #F3F4F6 100%)',
                                    borderRadius: '16px',
                                    border: '2px solid #E5E7EB'
                                }}
                                title={badge.description}
                            >
                                <div className="text-4xl mb-3">{badge.icon}</div>
                                <p className="text-sm font-bold" style={{ color: '#1F2937' }}>{badge.name}</p>
                                <p className="text-xs mt-1" style={{ color: '#6B7280' }}>{badge.description}</p>
                                {badge.earned_at && (
                                    <p className="text-xs mt-2 font-medium" style={{ color: '#9CA3AF' }}>
                                        {new Date(badge.earned_at).toLocaleDateString()}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Activity Heatmap - Cleaner design */}
            <div className="bg-white p-8" style={{
                borderRadius: '20px',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.06)'
            }}>
                <div className="flex items-center gap-3 mb-2">
                    <div className="flex items-center justify-center" style={{
                        width: '40px',
                        height: '40px',
                        background: 'linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)',
                        borderRadius: '10px'
                    }}>
                        <span className="text-xl">📊</span>
                    </div>
                    <h3 className="text-xl font-bold" style={{ color: '#1F2937' }}>
                        Activity Heatmap
                    </h3>
                </div>
                <p className="text-sm mb-6 ml-13" style={{ color: '#6B7280', marginLeft: '52px' }}>
                    Your practice activity over the past 6 months
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

    // Get color intensity based on questions solved - gradient from gray to green
    const getColorStyle = (day) => {
        if (!day) return { backgroundColor: '#F3F4F6' };
        if (day.isFuture) return { backgroundColor: '#F3F4F6', opacity: 0.4 };

        const { questions } = day;
        if (questions === 0) return { backgroundColor: '#F3F4F6' };
        if (questions <= 3) return { backgroundColor: '#BBF7D0' }; // Light green
        if (questions <= 6) return { backgroundColor: '#4ADE80' }; // Medium green
        if (questions <= 9) return { backgroundColor: '#16A34A' }; // Darker green
        return { backgroundColor: '#15803D' }; // Full dark green
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
                                    boxShadow: day.questions > 0 ? '0 1px 3px rgba(22, 163, 74, 0.3)' : 'none'
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


