import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Signup from './components/Signup';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import VerifyEmail from './components/VerifyEmail';
import PracticeSet from './components/PracticeSet';
import QuestionBank from './components/QuestionBank';
import QuestionDetail from './components/QuestionDetail';
import CreateBattle from './components/CreateBattle';
import BattleRoom from './components/BattleRoom';
import JoinBattle from './components/JoinBattle';
import BattleHistory from './components/BattleHistory';
import Settings from './components/Settings';
import AdminDashboard from './components/AdminDashboard';
import AdminUsers from './components/AdminUsers';
import AdminQuestions from './components/AdminQuestions';
import AdminLogs from './components/AdminLogs';
import AdminReports from './components/AdminReports';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="min-h-screen bg-gray-100">
                    <Routes>
                        <Route path="/" element={<Navigate to="/login" />} />
                        <Route path="/signup" element={<Signup />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/verify" element={<VerifyEmail />} />
                        <Route
                            path="/dashboard"
                            element={
                                <ProtectedRoute>
                                    <Dashboard />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/practice"
                            element={
                                <ProtectedRoute>
                                    <PracticeSet />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/question-bank"
                            element={
                                <ProtectedRoute>
                                    <QuestionBank />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/question/:questionId"
                            element={
                                <ProtectedRoute>
                                    <QuestionDetail />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/battle/create"
                            element={
                                <ProtectedRoute>
                                    <CreateBattle />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/battle/history"
                            element={
                                <ProtectedRoute>
                                    <BattleHistory />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/battle/join/:roomCode"
                            element={
                                <ProtectedRoute>
                                    <JoinBattle />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/battle/:roomCode"
                            element={
                                <ProtectedRoute>
                                    <BattleRoom />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/settings"
                            element={
                                <ProtectedRoute>
                                    <Settings />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/admin"
                            element={
                                <ProtectedRoute>
                                    <AdminDashboard />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/admin/users"
                            element={
                                <ProtectedRoute>
                                    <AdminUsers />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/admin/questions"
                            element={
                                <ProtectedRoute>
                                    <AdminQuestions />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/admin/logs"
                            element={
                                <ProtectedRoute>
                                    <AdminLogs />
                                </ProtectedRoute>
                            }
                        />
                        <Route
                            path="/admin/reports"
                            element={
                                <ProtectedRoute>
                                    <AdminReports />
                                </ProtectedRoute>
                            }
                        />
                    </Routes>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;
