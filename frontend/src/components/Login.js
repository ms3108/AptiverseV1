import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import API_URL from '../config/api';
import { Container, Form, Button, Alert, Spinner, Card } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { FaEnvelope, FaLock, FaBullseye, FaExclamationCircle } from 'react-icons/fa';
import toast from 'react-hot-toast';

function Login() {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
    });
    const [errors, setErrors] = useState({});
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { login } = useAuth();

    const validateForm = () => {
        const newErrors = {};

        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Email is invalid';
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
        if (errors[e.target.name]) {
            setErrors({
                ...errors,
                [e.target.name]: ''
            });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setMessage('');

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            const response = await axios.post(`${API_URL}/login`, {
                email: formData.email,
                password: formData.password
            });

            login(response.data.access_token);
            toast.success('Welcome back!');

            const userResponse = await axios.get(`${API_URL}/me`, {
                headers: { Authorization: `Bearer ${response.data.access_token}` }
            });

            if (userResponse.data.is_admin) {
                navigate('/admin');
            } else {
                navigate('/dashboard');
            }
        } catch (error) {
            if (error.response?.data?.detail) {
                setMessage(error.response.data.detail);
                toast.error(error.response.data.detail);
            } else {
                setMessage('Login failed. Please try again.');
                toast.error('Login failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-vh-100 d-flex align-items-center justify-content-center py-5 position-relative overflow-hidden"
            style={{
                background: '#FFFFFF',
            }}>
            {/* Animated Background Elements */}
            <motion.div
                className="position-absolute"
                style={{
                    top: '-10%',
                    right: '-5%',
                    width: '400px',
                    height: '400px',
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: '50%',
                    filter: 'blur(40px)'
                }}
                animate={{
                    scale: [1, 1.2, 1],
                    opacity: [0.1, 0.15, 0.1]
                }}
                transition={{
                    duration: 8,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
            />
            <motion.div
                className="position-absolute"
                style={{
                    bottom: '-15%',
                    left: '-10%',
                    width: '500px',
                    height: '500px',
                    background: 'rgba(255,255,255,0.08)',
                    borderRadius: '50%',
                    filter: 'blur(60px)'
                }}
                animate={{
                    scale: [1, 1.3, 1],
                    opacity: [0.08, 0.12, 0.08]
                }}
                transition={{
                    duration: 10,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
            />

            <Container>
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6, ease: "easeOut" }}
                    className="d-flex justify-content-center"
                >
                    <Card className="border-0 shadow-lg" style={{
                        maxWidth: '440px',
                        width: '100%',
                        borderRadius: '24px',
                        background: 'rgba(255, 255, 255, 0.95)',
                        backdropFilter: 'blur(20px)'
                    }}>
                        <Card.Body className="p-5">
                            {/* Logo */}
                            <motion.div
                                className="text-center mb-4"
                                initial={{ scale: 0 }}
                                animate={{ scale: 1 }}
                                transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                            >
                                <div className="d-inline-flex align-items-center justify-content-center rounded-4 mb-3"
                                    style={{
                                        width: '70px',
                                        height: '70px',
                                        background: '#2563EB',
                                        boxShadow: '0 10px 30px rgba(30, 136, 229, 0.4)'
                                    }}>
                                    <FaBullseye size={32} color="white" />
                                </div>
                                <h2 className="fw-bold mb-1" style={{
                                    background: 'linear-gradient(135deg, #1565C0 0%, #1E88E5 100%)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent',
                                    fontSize: '1.75rem'
                                }}>
                                    Welcome Back
                                </h2>
                                <p className="text-muted small mb-0">Sign in to continue your learning journey</p>
                            </motion.div>

                            <Form onSubmit={handleSubmit}>
                                {/* Email Input */}
                                <Form.Group className="mb-4">
                                    <Form.Label className="fw-semibold text-secondary small">Email address</Form.Label>
                                    <div className="position-relative">
                                        <div className="position-absolute d-flex align-items-center h-100 ps-3" style={{ color: '#94A3B8' }}>
                                            <FaEnvelope />
                                        </div>
                                        <Form.Control
                                            type="email"
                                            name="email"
                                            value={formData.email}
                                            onChange={handleChange}
                                            placeholder="you@example.com"
                                            className="ps-5 py-3"
                                            style={{
                                                borderRadius: '12px',
                                                border: errors.email ? '2px solid #EF4444' : '2px solid #E2E8F0',
                                                fontSize: '0.95rem'
                                            }}
                                            isInvalid={!!errors.email}
                                        />
                                    </div>
                                    {errors.email && (
                                        <motion.div
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="d-flex align-items-center gap-1 mt-2 text-danger small"
                                        >
                                            <FaExclamationCircle size={12} /> {errors.email}
                                        </motion.div>
                                    )}
                                </Form.Group>

                                {/* Password Input */}
                                <Form.Group className="mb-4">
                                    <Form.Label className="fw-semibold text-secondary small">Password</Form.Label>
                                    <div className="position-relative">
                                        <div className="position-absolute d-flex align-items-center h-100 ps-3" style={{ color: '#94A3B8' }}>
                                            <FaLock />
                                        </div>
                                        <Form.Control
                                            type="password"
                                            name="password"
                                            value={formData.password}
                                            onChange={handleChange}
                                            placeholder="••••••••"
                                            className="ps-5 py-3"
                                            style={{
                                                borderRadius: '12px',
                                                border: errors.password ? '2px solid #EF4444' : '2px solid #E2E8F0',
                                                fontSize: '0.95rem'
                                            }}
                                            isInvalid={!!errors.password}
                                        />
                                    </div>
                                    {errors.password && (
                                        <motion.div
                                            initial={{ opacity: 0, y: -10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            className="d-flex align-items-center gap-1 mt-2 text-danger small"
                                        >
                                            <FaExclamationCircle size={12} /> {errors.password}
                                        </motion.div>
                                    )}
                                </Form.Group>

                                {/* Error Message */}
                                {message && (
                                    <motion.div
                                        initial={{ opacity: 0, scale: 0.95 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                    >
                                        <Alert variant="danger" className="d-flex align-items-center gap-2 rounded-3 py-3">
                                            <FaExclamationCircle />
                                            {message}
                                        </Alert>
                                    </motion.div>
                                )}

                                {/* Submit Button */}
                                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                                    <Button
                                        type="submit"
                                        disabled={loading}
                                        className="w-100 py-3 fw-semibold border-0"
                                        style={{
                                            background: loading ? '#9CA3AF' : '#2563EB',
                                            borderRadius: '12px',
                                            boxShadow: loading ? 'none' : '0 10px 30px rgba(30, 136, 229, 0.4)',
                                            fontSize: '1rem'
                                        }}
                                    >
                                        {loading ? (
                                            <span className="d-flex align-items-center justify-content-center gap-2">
                                                <Spinner animation="border" size="sm" />
                                                Signing in...
                                            </span>
                                        ) : 'Sign in'}
                                    </Button>
                                </motion.div>

                                {/* Sign Up Link */}
                                <div className="text-center mt-4">
                                    <p className="text-muted small mb-0">
                                        Don't have an account?{' '}
                                        <Link to="/signup" className="fw-semibold text-decoration-none" style={{ color: '#2563EB' }}>
                                            Create one now
                                        </Link>
                                    </p>
                                </div>
                            </Form>
                        </Card.Body>
                    </Card>
                </motion.div>
            </Container>
        </div>
    );
}

export default Login;
