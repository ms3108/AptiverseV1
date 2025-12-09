import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { motion } from 'framer-motion';
import { FaEnvelope, FaLock, FaUser, FaUserPlus, FaArrowRight, FaExclamationCircle, FaCheckCircle } from 'react-icons/fa';
import axios from 'axios';
import API_URL from '../config/api';

function Signup() {
    const [formData, setFormData] = useState({
        email: '',
        username: '',
        password: '',
        confirmPassword: ''
    });
    const [errors, setErrors] = useState({});
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const validateForm = () => {
        const newErrors = {};

        if (!formData.email) {
            newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            newErrors.email = 'Email is invalid';
        }

        if (!formData.username) {
            newErrors.username = 'Username is required';
        } else if (formData.username.length < 3) {
            newErrors.username = 'Username must be at least 3 characters';
        }

        if (!formData.password) {
            newErrors.password = 'Password is required';
        } else if (formData.password.length < 8) {
            newErrors.password = 'Password must be at least 8 characters';
        }

        if (formData.password !== formData.confirmPassword) {
            newErrors.confirmPassword = 'Passwords do not match';
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
            const response = await axios.post(`${API_URL}/register`, {
                email: formData.email,
                username: formData.username,
                password: formData.password
            });

            setMessage('Registration successful! Please check your email to verify your account.');
            setTimeout(() => {
                navigate('/login');
            }, 3000);
        } catch (error) {
            if (error.response?.data?.detail) {
                setMessage(error.response.data.detail);
            } else {
                setMessage('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-vh-100 d-flex align-items-center justify-content-center py-5" style={{
            background: 'linear-gradient(135deg, #000000 0%, #1a1a1a 50%, #2d2d2d 100%)',
            position: 'relative',
            overflow: 'hidden'
        }}>
            {/* Background decorations */}
            <div style={{
                position: 'absolute',
                top: '10%',
                left: '-5%',
                width: '350px',
                height: '350px',
                background: 'rgba(255,255,255,0.08)',
                borderRadius: '50%',
                filter: 'blur(50px)'
            }}></div>
            <div style={{
                position: 'absolute',
                bottom: '5%',
                right: '-10%',
                width: '450px',
                height: '450px',
                background: 'rgba(255,255,255,0.06)',
                borderRadius: '50%',
                filter: 'blur(60px)'
            }}></div>

            <Container>
                <Row className="justify-content-center">
                    <Col xs={12} sm={10} md={8} lg={5}>
                        <motion.div
                            initial={{ opacity: 0, y: 30 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.6, ease: 'easeOut' }}
                        >
                            <Card className="border-0 shadow-lg" style={{
                                background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                                backdropFilter: 'blur(20px)',
                                borderRadius: '20px'
                            }}>
                                <Card.Body className="p-4 p-md-5">
                                    {/* Logo/Icon */}
                                    <motion.div
                                        className="text-center mb-4"
                                        initial={{ scale: 0 }}
                                        animate={{ scale: 1 }}
                                        transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                                    >
                                        <div className="d-inline-flex align-items-center justify-content-center mb-3" style={{
                                            width: '60px',
                                            height: '60px',
                                            background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                            borderRadius: '16px',
                                            boxShadow: '0 10px 30px rgba(13, 71, 161, 0.4)'
                                        }}>
                                            <FaUserPlus className="text-white fs-4" />
                                        </div>
                                        <h2 className="fw-bold mb-1" style={{
                                            background: 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                            WebkitBackgroundClip: 'text',
                                            WebkitTextFillColor: 'transparent'
                                        }}>
                                            Join Aptiverse
                                        </h2>
                                        <p className="text-muted small">Start your learning journey today</p>
                                    </motion.div>

                                    <Form onSubmit={handleSubmit}>
                                        {/* Email Field */}
                                        <motion.div
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.3 }}
                                        >
                                            <Form.Group className="mb-3">
                                                <Form.Label className="fw-semibold text-dark small">Email address</Form.Label>
                                                <div className="position-relative">
                                                    <div className="position-absolute top-50 translate-middle-y ms-3" style={{ color: '#6B7280' }}>
                                                        <FaEnvelope />
                                                    </div>
                                                    <Form.Control
                                                        type="email"
                                                        name="email"
                                                        value={formData.email}
                                                        onChange={handleChange}
                                                        placeholder="you@example.com"
                                                        className="py-3 ps-5"
                                                        isInvalid={!!errors.email}
                                                        style={{
                                                            borderRadius: '12px',
                                                            border: errors.email ? '2px solid #dc3545' : '2px solid #E2E8F0',
                                                            backgroundColor: '#F8FAFC'
                                                        }}
                                                    />
                                                </div>
                                                {errors.email && (
                                                    <small className="text-danger d-flex align-items-center mt-1">
                                                        <FaExclamationCircle className="me-1" /> {errors.email}
                                                    </small>
                                                )}
                                            </Form.Group>
                                        </motion.div>

                                        {/* Username Field */}
                                        <motion.div
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.35 }}
                                        >
                                            <Form.Group className="mb-3">
                                                <Form.Label className="fw-semibold text-dark small">Username</Form.Label>
                                                <div className="position-relative">
                                                    <div className="position-absolute top-50 translate-middle-y ms-3" style={{ color: '#6B7280' }}>
                                                        <FaUser />
                                                    </div>
                                                    <Form.Control
                                                        type="text"
                                                        name="username"
                                                        value={formData.username}
                                                        onChange={handleChange}
                                                        placeholder="Choose a username"
                                                        className="py-3 ps-5"
                                                        isInvalid={!!errors.username}
                                                        style={{
                                                            borderRadius: '12px',
                                                            border: errors.username ? '2px solid #dc3545' : '2px solid #E2E8F0',
                                                            backgroundColor: '#F8FAFC'
                                                        }}
                                                    />
                                                </div>
                                                {errors.username && (
                                                    <small className="text-danger d-flex align-items-center mt-1">
                                                        <FaExclamationCircle className="me-1" /> {errors.username}
                                                    </small>
                                                )}
                                            </Form.Group>
                                        </motion.div>

                                        {/* Password Field */}
                                        <motion.div
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.4 }}
                                        >
                                            <Form.Group className="mb-3">
                                                <Form.Label className="fw-semibold text-dark small">Password</Form.Label>
                                                <div className="position-relative">
                                                    <div className="position-absolute top-50 translate-middle-y ms-3" style={{ color: '#6B7280' }}>
                                                        <FaLock />
                                                    </div>
                                                    <Form.Control
                                                        type="password"
                                                        name="password"
                                                        value={formData.password}
                                                        onChange={handleChange}
                                                        placeholder="••••••••"
                                                        className="py-3 ps-5"
                                                        isInvalid={!!errors.password}
                                                        style={{
                                                            borderRadius: '12px',
                                                            border: errors.password ? '2px solid #dc3545' : '2px solid #E2E8F0',
                                                            backgroundColor: '#F8FAFC'
                                                        }}
                                                    />
                                                </div>
                                                {errors.password && (
                                                    <small className="text-danger d-flex align-items-center mt-1">
                                                        <FaExclamationCircle className="me-1" /> {errors.password}
                                                    </small>
                                                )}
                                            </Form.Group>
                                        </motion.div>

                                        {/* Confirm Password Field */}
                                        <motion.div
                                            initial={{ opacity: 0, x: -20 }}
                                            animate={{ opacity: 1, x: 0 }}
                                            transition={{ delay: 0.45 }}
                                        >
                                            <Form.Group className="mb-4">
                                                <Form.Label className="fw-semibold text-dark small">Confirm Password</Form.Label>
                                                <div className="position-relative">
                                                    <div className="position-absolute top-50 translate-middle-y ms-3" style={{ color: '#6B7280' }}>
                                                        <FaLock />
                                                    </div>
                                                    <Form.Control
                                                        type="password"
                                                        name="confirmPassword"
                                                        value={formData.confirmPassword}
                                                        onChange={handleChange}
                                                        placeholder="••••••••"
                                                        className="py-3 ps-5"
                                                        isInvalid={!!errors.confirmPassword}
                                                        style={{
                                                            borderRadius: '12px',
                                                            border: errors.confirmPassword ? '2px solid #dc3545' : '2px solid #E2E8F0',
                                                            backgroundColor: '#F8FAFC'
                                                        }}
                                                    />
                                                </div>
                                                {errors.confirmPassword && (
                                                    <small className="text-danger d-flex align-items-center mt-1">
                                                        <FaExclamationCircle className="me-1" /> {errors.confirmPassword}
                                                    </small>
                                                )}
                                            </Form.Group>
                                        </motion.div>

                                        {/* Message Alert */}
                                        {message && (
                                            <motion.div
                                                initial={{ opacity: 0, scale: 0.9 }}
                                                animate={{ opacity: 1, scale: 1 }}
                                            >
                                                <Alert
                                                    variant={message.includes('successful') ? 'success' : 'danger'}
                                                    className="d-flex align-items-center rounded-3 mb-4"
                                                >
                                                    {message.includes('successful') ? (
                                                        <FaCheckCircle className="me-2" />
                                                    ) : (
                                                        <FaExclamationCircle className="me-2" />
                                                    )}
                                                    {message}
                                                </Alert>
                                            </motion.div>
                                        )}

                                        {/* Submit Button */}
                                        <motion.div
                                            initial={{ opacity: 0, y: 20 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.5 }}
                                        >
                                            <Button
                                                type="submit"
                                                disabled={loading}
                                                className="w-100 py-3 fw-semibold border-0 d-flex align-items-center justify-content-center gap-2"
                                                style={{
                                                    background: loading ? '#9CA3AF' : 'linear-gradient(135deg, #000000 0%, #333333 100%)',
                                                    borderRadius: '12px',
                                                    boxShadow: loading ? 'none' : '0 10px 30px rgba(13, 71, 161, 0.4)',
                                                    transition: 'all 0.3s ease'
                                                }}
                                            >
                                                {loading ? (
                                                    <>
                                                        <Spinner animation="border" size="sm" />
                                                        Creating account...
                                                    </>
                                                ) : (
                                                    <>
                                                        Create Account
                                                        <FaArrowRight />
                                                    </>
                                                )}
                                            </Button>
                                        </motion.div>

                                        {/* Sign In Link */}
                                        <motion.div
                                            className="text-center mt-4"
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: 0.6 }}
                                        >
                                            <p className="text-muted small mb-0">
                                                Already have an account?{' '}
                                                <Link to="/login" className="fw-semibold text-decoration-none" style={{ color: '#000000' }}>
                                                    Sign in
                                                </Link>
                                            </p>
                                        </motion.div>
                                    </Form>
                                </Card.Body>
                            </Card>
                        </motion.div>
                    </Col>
                </Row>
            </Container>
        </div>
    );
}

export default Signup;
