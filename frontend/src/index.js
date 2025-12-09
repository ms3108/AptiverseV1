import React from 'react';
import ReactDOM from 'react-dom/client';
import 'bootstrap/dist/css/bootstrap.min.css';
import './index.css';
import App from './App';
import { Toaster } from 'react-hot-toast';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <React.StrictMode>
        <Toaster
            position="top-right"
            toastOptions={{
                duration: 3000,
                style: {
                    background: '#1E40AF',
                    color: '#fff',
                    borderRadius: '12px',
                    padding: '16px',
                },
                success: {
                    iconTheme: {
                        primary: '#60A5FA',
                        secondary: '#fff',
                    },
                },
            }}
        />
        <App />
    </React.StrictMode>
);
