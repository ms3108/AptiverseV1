// API Configuration
import axios from 'axios';

export const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Configure axios defaults for better performance
axios.defaults.timeout = 15000; // 15 second timeout
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Add request interceptor for performance monitoring
axios.interceptors.request.use(
    (config) => {
        config.metadata = { startTime: new Date() };
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Add response interceptor for performance monitoring
axios.interceptors.response.use(
    (response) => {
        const endTime = new Date();
        const duration = endTime - response.config.metadata.startTime;
        console.log(`API call to ${response.config.url} took ${duration}ms`);
        return response;
    },
    (error) => {
        if (error.code === 'ECONNABORTED') {
            console.error('Request timeout - server may be slow');
        }
        return Promise.reject(error);
    }
);

export default API_URL;
