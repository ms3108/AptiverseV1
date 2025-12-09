import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Spinner, Alert, Badge, ProgressBar } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { FaFire, FaBolt, FaCheckCircle, FaTrophy, FaChartBar } from 'react-icons/fa';
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
            <div className="d-flex justify-content-center align-items-center p-5">
                <Spinner animation="border" style={{ color: '#93C5FD', width: '3rem', height: '3rem' }} />
            </div>
        );
    }

    if (error) {
        return (
            <Alert variant="danger" className="rounded-3">
                {error}
            </Alert>
        );
    }

    if (!stats) return null;

    const xpPercentage = (stats.xp_progress / (stats.xp_for_next_level - (stats.level * 100))) * 100;

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: { staggerChildren: 0.1 }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
    };

    return (
        <motion.div
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            className="d-flex flex-column gap-4"
        >
            {/* User Header */}
            <motion.div variants={itemVariants}>
                <Card className="border-0 shadow-sm" style={{ borderRadius: '16px' }}>
                    <Card.Body className="p-4">
                        <h2 className="fw-bold mb-1" style={{ color: '#1F2937' }}>
                            Welcome back, {stats.username}!
                        </h2>
                        <p className="text-muted mb-0">Ready to level up your skills today?</p>
                    </Card.Body>
                </Card>
            </motion.div>

            {/* XP and Level Progress */}
            <motion.div variants={itemVariants}>
                <Card className="border-0 text-white" style={{
                    borderRadius: '16px',
                    background: 'linear-gradient(135deg, #93C5FD 0%, #BFDBFE 100%)',
                    boxShadow: '0 4px 20px rgba(147, 197, 253, 0.3)'
                }}>
                    <Card.Body className="p-4">
                        <Row className="align-items-center mb-4">
                            <Col xs="auto">
                                <div className="d-flex align-items-center gap-3">
                                    {/* Level Badge */}
                                    <div className="d-flex align-items-center justify-content-center" style={{
                                        width: '64px',
                                        height: '64px',
                                        background: 'rgba(255, 255, 255, 0.2)',
                                        borderRadius: '14px',
                                        border: '2px solid rgba(255, 255, 255, 0.3)'
                                    }}>
                                        <span className="display-6 fw-bold">{stats.level}</span>
                                    </div>
                                    <div>
                                        <small style={{ color: 'rgba(255,255,255,0.7)' }}>Current XP</small>
                                        <h2 className="mb-0 fw-bold">{stats.xp}</h2>
                                    </div>
                                </div>
                            </Col>
                            <Col className="text-end">
                                <small style={{ color: 'rgba(255,255,255,0.7)' }}>Next Level</small>
                                <h2 className="mb-0 fw-bold" style={{ color: '#BFDBFE' }}>{stats.xp_for_next_level}</h2>
                            </Col>
                        </Row>

                        {/* Progress Bar */}
                        <ProgressBar
                            now={Math.min(xpPercentage, 100)}
                            style={{
                                height: '12px',
                                backgroundColor: 'rgba(255,255,255,0.2)',
                                borderRadius: '6px'
                            }}
                            variant="info"
                        />
                        <small className="d-block mt-2" style={{ color: 'rgba(255,255,255,0.8)' }}>
                            {stats.xp_progress} / {stats.xp_for_next_level - (stats.level * 100)} XP to Level {stats.level + 1}
                        </small>
                    </Card.Body>
                </Card>
            </motion.div>

            {/* Stats Grid */}
            <Row className="g-3">
                {/* Current Streak */}
                <Col md={4}>
                    <motion.div variants={itemVariants}>
                        <Card className="border-0 shadow-sm h-100" style={{ borderRadius: '16px' }}>
                            <Card.Body className="p-4">
                                <div className="d-flex align-items-center gap-3 mb-3">
                                    <div className="d-flex align-items-center justify-content-center" style={{
                                        width: '40px',
                                        height: '40px',
                                        backgroundColor: '#EFF6FF',
                                        borderRadius: '10px'
                                    }}>
                                        <FaFire className="text-warning" />
                                    </div>
                                    <span className="text-muted small">Current Streak</span>
                                </div>
                                <h2 className="fw-bold mb-0" style={{ color: '#60A5FA' }}>
                                    {stats.current_streak}
                                </h2>
                                <small className="text-muted">days</small>
                            </Card.Body>
                        </Card>
                    </motion.div>
                </Col>

                {/* Longest Streak */}
                <Col md={4}>
                    <motion.div variants={itemVariants}>
                        <Card className="border-0 shadow-sm h-100" style={{ borderRadius: '16px' }}>
                            <Card.Body className="p-4">
                                <div className="d-flex align-items-center gap-3 mb-3">
                                    <div className="d-flex align-items-center justify-content-center" style={{
                                        width: '40px',
                                        height: '40px',
                                        backgroundColor: '#F0F9FF',
                                        borderRadius: '10px'
                                    }}>
                                        <FaBolt style={{ color: '#93C5FD' }} />
                                    </div>
                                    <span className="text-muted small">Best Streak</span>
                                </div>
                                <h2 className="fw-bold mb-0" style={{ color: '#60A5FA' }}>
                                    {stats.longest_streak}
                                </h2>
                                <small className="text-muted">personal best</small>
                            </Card.Body>
                        </Card>
                    </motion.div>
                </Col>

                {/* Total Questions */}
                <Col md={4}>
                    <motion.div variants={itemVariants}>
                        <Card className="border-0 shadow-sm h-100" style={{ borderRadius: '16px' }}>
                            <Card.Body className="p-4">
                                <div className="d-flex align-items-center gap-3 mb-3">
                                    <div className="d-flex align-items-center justify-content-center" style={{
                                        width: '40px',
                                        height: '40px',
                                        backgroundColor: '#F0F9FF',
                                        borderRadius: '10px'
                                    }}>
                                        <FaCheckCircle style={{ color: '#93C5FD' }} />
                                    </div>
                                    <span className="text-muted small">Solved</span>
                                </div>
                                <h2 className="fw-bold mb-0" style={{ color: '#60A5FA' }}>
                                    {stats.total_questions_solved}
                                </h2>
                                <small className="text-muted">questions</small>
                            </Card.Body>
                        </Card>
                    </motion.div>
                </Col>
            </Row>

            {/* Badges Section */}
            {stats.badges && stats.badges.length > 0 && (
                <motion.div variants={itemVariants}>
                    <Card className="border-0 shadow-sm" style={{ borderRadius: '16px' }}>
                        <Card.Body className="p-4">
                            <div className="d-flex align-items-center gap-3 mb-4">
                                <div className="d-flex align-items-center justify-content-center" style={{
                                    width: '40px',
                                    height: '40px',
                                    backgroundColor: '#EFF6FF',
                                    borderRadius: '10px'
                                }}>
                                    <FaTrophy style={{ color: '#F59E0B' }} />
                                </div>
                                <h5 className="mb-0 fw-semibold" style={{ color: '#1F2937' }}>
                                    Achievements ({stats.badges.length})
                                </h5>
                            </div>
                            <Row className="g-3">
                                {stats.badges.map((badge, index) => (
                                    <Col xs={6} md={3} key={index}>
                                        <motion.div
                                            whileHover={{ scale: 1.05 }}
                                            className="p-3 text-center rounded-3"
                                            style={{
                                                backgroundColor: '#F9FAFB',
                                                border: '1px solid #E5E7EB'
                                            }}
                                            title={badge.description}
                                        >
                                            <div className="fs-1 mb-2">{badge.icon}</div>
                                            <p className="small fw-semibold mb-1" style={{ color: '#1F2937' }}>{badge.name}</p>
                                            <small className="text-muted">{badge.description}</small>
                                        </motion.div>
                                    </Col>
                                ))}
                            </Row>
                        </Card.Body>
                    </Card>
                </motion.div>
            )}

            {/* Activity Heatmap */}
            <motion.div variants={itemVariants}>
                <Card className="border-0 shadow-sm" style={{ borderRadius: '16px' }}>
                    <Card.Body className="p-4">
                        <div className="d-flex align-items-center gap-3 mb-2">
                            <div className="d-flex align-items-center justify-content-center" style={{
                                width: '40px',
                                height: '40px',
                                backgroundColor: '#EFF6FF',
                                borderRadius: '10px'
                            }}>
                                <FaChartBar style={{ color: '#93C5FD' }} />
                            </div>
                            <h5 className="mb-0 fw-semibold" style={{ color: '#1F2937' }}>
                                Activity
                            </h5>
                        </div>
                        <p className="text-muted small mb-4" style={{ marginLeft: '52px' }}>
                            Your practice activity over the past 6 months
                        </p>
                        <ActivityHeatmap activityData={stats.activity_data} />
                    </Card.Body>
                </Card>
            </motion.div>
        </motion.div>
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
        if (questions <= 3) return { backgroundColor: '#DBEAFE' }; // Very light blue
        if (questions <= 6) return { backgroundColor: '#BFDBFE' }; // Light blue
        if (questions <= 9) return { backgroundColor: '#93C5FD' }; // Medium blue
        return { backgroundColor: '#60A5FA' }; // Darker blue
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
                                    boxShadow: day.questions > 0 ? '0 1px 3px rgba(147, 197, 253, 0.3)' : 'none'
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
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#DBEAFE' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#BFDBFE' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#93C5FD' }}></div>
                    <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: '#60A5FA' }}></div>
                </div>
                <span>More</span>
            </div>
        </div>
    );
}

export default DashboardStats;


