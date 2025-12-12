import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Navbar, Nav, Container, Button, Badge } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { FaHome, FaBookOpen, FaChartPie, FaUsers, FaQuestionCircle, FaCrown, FaExclamationTriangle, FaSignOutAlt } from 'react-icons/fa';
import { GiCrossedSwords } from 'react-icons/gi';
import { useAuth } from '../context/AuthContext';
import WarningsModal from './WarningsModal';
import API_URL from '../config/api';

function Navigation() {
    const navigate = useNavigate();
    const { user, logout } = useAuth();
    const isAdmin = user?.is_admin;
    const [warningsCount, setWarningsCount] = useState(0);
    const [showWarningsModal, setShowWarningsModal] = useState(false);

    useEffect(() => {
        if (!isAdmin && user) {
            fetchWarningsCount();
        }
    }, [user, isAdmin]);

    const fetchWarningsCount = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/warnings`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setWarningsCount(data.unread || 0);
            }
        } catch (error) {
            console.error('Error fetching warnings:', error);
        }
    };

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const NavButton = ({ onClick, variant = "outline", icon, children, style = {} }) => (
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Button
                onClick={onClick}
                variant=""
                className="d-flex align-items-center gap-2 fw-semibold"
                style={{
                    borderRadius: '10px',
                    background: variant === "outline"
                        ? '#ffffff'
                        : 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                    border: variant === "outline" ? '2px solid #000000' : 'none',
                    color: variant === "outline" ? '#000000' : '#ffffff',
                    padding: '8px 16px',
                    fontSize: '14px',
                    boxShadow: variant === "outline"
                        ? '0 2px 4px rgba(0, 0, 0, 0.1)'
                        : '0 4px 8px rgba(0, 0, 0, 0.3)',
                    ...style
                }}
            >
                {icon}
                {children}
            </Button>
        </motion.div>
    );

    return (
        <Navbar bg="" expand="lg" className="border-bottom shadow-sm py-2" style={{
            borderColor: '#E2E8F0',
            background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)'
        }}>
            <Container fluid className="px-4">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                >
                    <Navbar.Brand
                        onClick={() => navigate(isAdmin ? '/admin' : '/dashboard')}
                        className="fw-bold fs-4"
                        style={{
                            cursor: 'pointer',
                            color: '#000000',
                            background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            letterSpacing: '-0.5px'
                        }}
                    >
                        Aptiverse
                    </Navbar.Brand>
                </motion.div>

                <Navbar.Toggle aria-controls="basic-navbar-nav" />

                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="me-auto d-flex flex-row flex-wrap gap-2 mt-2 mt-lg-0 ms-lg-3">
                        {!isAdmin && (
                            <NavButton onClick={() => navigate('/dashboard')} icon={<FaHome />}>
                                Dashboard
                            </NavButton>
                        )}
                    </Nav>

                    <Nav className="d-flex flex-row flex-wrap align-items-center gap-2">
                        {!isAdmin && (
                            <>
                                <NavButton
                                    onClick={() => navigate('/practice')}
                                    variant="solid"
                                    icon={<FaChartPie />}
                                    style={{
                                        background: 'linear-gradient(135deg, #1a1a1a 0%, #000000 100%)',
                                        boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.4)'
                                    }}
                                >
                                    Today's Practice
                                </NavButton>
                                <NavButton
                                    onClick={() => {
                                        navigate('/question-bank', { replace: true });
                                        window.location.href = '/question-bank';
                                    }}
                                    icon={<FaBookOpen />}
                                >
                                    Question Bank
                                </NavButton>
                                <NavButton
                                    onClick={() => navigate('/battle/history')}
                                    icon={<GiCrossedSwords />}
                                >
                                    Battles
                                </NavButton>
                            </>
                        )}

                        {isAdmin && (
                            <>
                                <NavButton
                                    onClick={() => navigate('/admin')}
                                    variant="solid"
                                    icon={<FaCrown />}
                                    style={{
                                        background: 'linear-gradient(135deg, #1a1a1a 0%, #000000 100%)',
                                        boxShadow: '0px 4px 10px rgba(0, 0, 0, 0.4)'
                                    }}
                                >
                                    Admin Dashboard
                                </NavButton>
                                <NavButton onClick={() => navigate('/admin/users')} icon={<FaUsers />}>
                                    Users
                                </NavButton>
                                <NavButton
                                    onClick={() => navigate('/admin/questions')}
                                    icon={<FaQuestionCircle />}
                                >
                                    Questions
                                </NavButton>
                            </>
                        )}

                        {!isAdmin && warningsCount > 0 && (
                            <motion.div whileHover={{ scale: 1.05 }} className="position-relative">
                                <Button
                                    onClick={() => setShowWarningsModal(true)}
                                    variant=""
                                    className="d-flex align-items-center gap-2 fw-semibold"
                                    style={{
                                        borderRadius: '10px',
                                        background: 'linear-gradient(135deg, #fff7ed 0%, #fed7aa 100%)',
                                        border: '2px solid transparent',
                                        borderImage: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                                        borderImageSlice: 1,
                                        color: '#92400e',
                                        padding: '8px 16px',
                                        fontSize: '14px',
                                        boxShadow: '0 2px 4px rgba(245, 158, 11, 0.2)'
                                    }}
                                >
                                    <FaExclamationTriangle />
                                    Warnings
                                </Button>
                                <Badge
                                    style={{
                                        background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                        color: 'white',
                                        top: '-8px',
                                        right: '-8px',
                                        animation: 'pulse 2s infinite'
                                    }}
                                    pill
                                    className="position-absolute"
                                >
                                    {warningsCount}
                                </Badge>
                            </motion.div>
                        )}

                        <span className="text-muted small d-none d-lg-inline mx-2">
                            Welcome, <span className="fw-semibold" style={{ color: '#000000' }}>{user?.username}</span>!
                        </span>

                        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                            <Button
                                onClick={handleLogout}
                                className="d-flex align-items-center gap-2 fw-semibold"
                                style={{
                                    background: 'linear-gradient(135deg, #1a1a1a 0%, #000000 100%)',
                                    border: 'none',
                                    borderRadius: '10px',
                                    padding: '8px 16px',
                                    fontSize: '14px',
                                    color: 'white',
                                    boxShadow: '0 4px 8px rgba(0, 0, 0, 0.4)'
                                }}
                            >
                                <FaSignOutAlt />
                                Logout
                            </Button>
                        </motion.div>
                    </Nav>
                </Navbar.Collapse>
            </Container>
            <WarningsModal
                isOpen={showWarningsModal}
                onClose={() => {
                    setShowWarningsModal(false);
                    fetchWarningsCount();
                }}
            />
        </Navbar>
    );
}

export default Navigation;
