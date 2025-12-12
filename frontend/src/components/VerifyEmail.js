import React, { useEffect, useState, useRef } from 'react';
import API_URL from '../config/api';
import { useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';

function VerifyEmail() {
    const [searchParams] = useSearchParams();
    const [status, setStatus] = useState('verifying'); // verifying, success, error
    const [message, setMessage] = useState('Verifying your email...');
    const token = searchParams.get('token');
    const hasVerified = useRef(false); // Prevent duplicate API calls

    useEffect(() => {
        if (token && !hasVerified.current) {
            hasVerified.current = true; // Mark as called
            verifyEmail();
        } else if (!token) {
            setStatus('error');
            setMessage('Invalid verification link');
        }
    }, [token]);

    const verifyEmail = async () => {
        try {
            const response = await axios.get(`${API_URL}/verify-email?token=${token}`);
            setStatus('success');
            setMessage(response.data.message);
        } catch (error) {
            // Check if it's an "already verified" error - treat as success
            if (error.response?.status === 400 &&
                error.response?.data?.detail &&
                error.response.data.detail.toLowerCase().includes('already verified')) {
                setStatus('success');
                setMessage('Email already verified. You can now log in.');
            } else {
                setStatus('error');
                if (error.response?.data?.detail) {
                    setMessage(error.response.data.detail);
                } else {
                    setMessage('Verification failed. Please try again.');
                }
            }
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-400 to-blue-700 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-10 rounded-xl shadow-2xl">
                <div className="text-center">
                    {status === 'verifying' && (
                        <div>
                            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto"></div>
                            <h2 className="mt-6 text-2xl font-bold text-gray-900">
                                Verifying your email...
                            </h2>
                            <p className="mt-2 text-sm text-gray-600">
                                Please wait while we verify your email address.
                            </p>
                        </div>
                    )}

                    {status === 'success' && (
                        <div>
                            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
                                <svg
                                    className="h-8 w-8 text-green-600"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth="2"
                                        d="M5 13l4 4L19 7"
                                    />
                                </svg>
                            </div>
                            <h2 className="mt-6 text-2xl font-bold text-gray-900">
                                Email Verified!
                            </h2>
                            <p className="mt-2 text-sm text-gray-600">{message}</p>
                            <div className="mt-6">
                                <Link
                                    to="/login"
                                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
                                >
                                    Go to Login
                                </Link>
                            </div>
                        </div>
                    )}

                    {status === 'error' && (
                        <div>
                            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100">
                                <svg
                                    className="h-8 w-8 text-red-600"
                                    fill="none"
                                    stroke="currentColor"
                                    viewBox="0 0 24 24"
                                >
                                    <path
                                        strokeLinecap="round"
                                        strokeLinejoin="round"
                                        strokeWidth="2"
                                        d="M6 18L18 6M6 6l12 12"
                                    />
                                </svg>
                            </div>
                            <h2 className="mt-6 text-2xl font-bold text-gray-900">
                                Verification Failed
                            </h2>
                            <p className="mt-2 text-sm text-gray-600">{message}</p>
                            <div className="mt-6 space-y-3">
                                <Link
                                    to="/signup"
                                    className="block w-full px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-black hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
                                >
                                    Sign Up Again
                                </Link>
                                <Link
                                    to="/login"
                                    className="block w-full px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-black"
                                >
                                    Back to Login
                                </Link>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default VerifyEmail;

