import React, { useState, useEffect } from 'react';
import API_URL from '../config/api';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import DashboardStats from './DashboardStats';
import NotificationsPanel from './NotificationsPanel';
import { Container, Navbar, Nav, Button, Badge, Dropdown } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { FaBell, FaSignOutAlt, FaBook, FaGamepad, FaBullseye, FaCog, FaUser } from 'react-icons/fa';
import toast from 'react-hot-toast';

function Dashboard() {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const [showNotifications, setShowNotifications] = useState(false);
    const [notificationCount, setNotificationCount] = useState(0);

    useEffect(() => {
        fetchNotificationCount();
        const interval = setInterval(fetchNotificationCount, 30000);
        return () => clearInterval(interval);
    }, []);

    const fetchNotificationCount = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/warnings`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (response.ok) {
                const data = await response.json();
                setNotificationCount(data.unread || 0);
            }
        } catch (error) {
            console.error('Error fetching notification count:', error);
        }
    };

    const handleLogout = () => {
        toast.success('Logged out successfully!');
        logout();
        navigate('/login');
    };

    const handleStartPractice = () => {
        navigate('/practice');
    };

    const handleQuestionBank = () => {
        navigate('/question-bank');
    };

    return (
        <div className="min-vh-100" style={{ background: '#FFFFFF' }}>
            {/* Modern Navbar */}
            <Navbar
                expand="lg"
                className="py-3 shadow-sm"
                style={{
                    background: 'rgba(255, 255, 255, 0.95)',
                    backdropFilter: 'blur(10px)',
                    borderBottom: '1px solid rgba(226, 232, 240, 0.8)'
                }}
                sticky="top"
            >
                <Container>
                    <Navbar.Brand
                        onClick={() => navigate('/dashboard')}
                        style={{ cursor: 'pointer' }}
                    >
                        <motion.h1
                            className="mb-0 fw-bold"
                            style={{
                                color: '#000000',
                                background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                fontSize: '1.75rem',
                                letterSpacing: '-0.5px'
                            }}
                            whileHover={{ scale: 1.05 }}
                            transition={{ type: "spring", stiffness: 400 }}
                        >
                            Aptiverse
                        </motion.h1>
                    </Navbar.Brand>

                    <Navbar.Toggle aria-controls="navbar-nav" />

                    <Navbar.Collapse id="navbar-nav">
                        <Nav className="ms-auto align-items-center gap-2">
                            {/* Practice Button */}
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                                <Button
                                    onClick={handleStartPractice}
                                    className="d-flex align-items-center gap-2 fw-semibold border-0"
                                    style={{
                                        background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                        boxShadow: '0 4px 14px rgba(0, 0, 0, 0.35)',
                                        borderRadius: '12px',
                                        padding: '10px 20px'
                                    }}
                                >
                                    <FaBullseye /> Practice
                                </Button>
                            </motion.div>

                            {/* Questions Button */}
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                                <Button
                                    onClick={handleQuestionBank}
                                    className="d-flex align-items-center gap-2 fw-semibold"
                                    style={{
                                        borderRadius: '12px',
                                        border: '2px solid #000000',
                                        backgroundColor: '#FFFFFF',
                                        color: '#000000',
                                        padding: '10px 20px'
                                    }}
                                >
                                    <FaBook /> Questions
                                </Button>
                            </motion.div>

                            {/* Battles Button */}
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                                <Button
                                    onClick={() => navigate('/battle/history')}
                                    className="d-flex align-items-center gap-2 fw-semibold"
                                    style={{
                                        borderRadius: '12px',
                                        border: '2px solid #000000',
                                        backgroundColor: '#FFFFFF',
                                        color: '#000000',
                                        padding: '10px 20px'
                                    }}
                                >
                                    <FaGamepad /> Battles
                                </Button>
                            </motion.div>

                            {/* Notification Bell */}
                            <motion.div
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                className="position-relative mx-2"
                            >
                                <Button
                                    variant="light"
                                    onClick={() => setShowNotifications(!showNotifications)}
                                    className="rounded-circle p-2 position-relative"
                                    style={{
                                        width: '44px',
                                        height: '44px',
                                        background: showNotifications ? 'rgba(30, 136, 229, 0.1)' : 'white',
                                        border: '2px solid #E2E8F0'
                                    }}
                                >
                                    <FaBell size={18} color="#000000" />
                                    {notificationCount > 0 && (
                                        <Badge
                                            pill
                                            className="position-absolute"
                                            style={{
                                                top: '-5px',
                                                right: '-5px',
                                                background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                                fontSize: '0.65rem',
                                                animation: 'pulse 2s infinite'
                                            }}
                                        >
                                            {notificationCount > 9 ? '9+' : notificationCount}
                                        </Badge>
                                    )}
                                </Button>
                            </motion.div>

                            {/* User Dropdown */}
                            <Dropdown align="end">
                                <Dropdown.Toggle
                                    variant="light"
                                    className="d-flex align-items-center gap-2 border-0"
                                    style={{
                                        background: 'rgba(30, 136, 229, 0.08)',
                                        borderRadius: '12px',
                                        padding: '8px 16px'
                                    }}
                                >
                                    <FaUser size={14} color="#000000" />
                                    <span className="fw-semibold" style={{ color: '#000000' }}>
                                        {user?.username}
                                    </span>
                                </Dropdown.Toggle>

                                <Dropdown.Menu
                                    className="shadow-lg border-0"
                                    style={{ borderRadius: '12px', padding: '8px' }}
                                >
                                    <Dropdown.Item
                                        onClick={() => navigate('/settings')}
                                        className="d-flex align-items-center gap-2 rounded-2 py-2"
                                    >
                                        <FaCog color="#64748B" /> Settings
                                    </Dropdown.Item>
                                    <Dropdown.Divider />
                                    <Dropdown.Item
                                        onClick={handleLogout}
                                        className="d-flex align-items-center gap-2 rounded-2 py-2 text-danger"
                                    >
                                        <FaSignOutAlt /> Logout
                                    </Dropdown.Item>
                                </Dropdown.Menu>
                            </Dropdown>
                        </Nav>
                    </Navbar.Collapse>
                </Container>
            </Navbar>

            {/* Main Content */}
            <Container className="py-4">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                >
                    <DashboardStats />
                </motion.div>
            </Container>

            {/* Notifications Panel */}
            <NotificationsPanel
                isOpen={showNotifications}
                onClose={() => {
                    setShowNotifications(false);
                    fetchNotificationCount();
                }}
            />
        </div >
    );
}

export default Dashboard;

