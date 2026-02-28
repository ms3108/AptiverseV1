import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import API_URL from '../config/api';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [token, setToken] = useState(localStorage.getItem('token'));

    useEffect(() => {
        if (token) {
            fetchUser();
        } else {
            setLoading(false);
        }
    }, []);

    const fetchUser = async (tokenToUse = token) => {
        try {
            const response = await axios.get(`${API_URL}/me`, {
                headers: {
                    Authorization: `Bearer ${tokenToUse}`
                }
            });
            setUser(response.data);
            return response.data;
        } catch (error) {
            console.error('Error fetching user:', error);
            localStorage.removeItem('token');
            setToken(null);
            setUser(null);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    const login = async (newToken) => {
        setLoading(true);
        localStorage.setItem('token', newToken);
        setToken(newToken);
        // Immediately fetch user data with the new token
        const userData = await fetchUser(newToken);
        return userData;
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, token, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};
