import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

const Signup = lazy(() => import('./components/Signup'));
const Login = lazy(() => import('./components/Login'));
const Dashboard = lazy(() => import('./components/Dashboard'));
const VerifyEmail = lazy(() => import('./components/VerifyEmail'));
const PracticeSet = lazy(() => import('./components/PracticeSet'));
const QuestionBank = lazy(() => import('./components/QuestionBank'));
const QuestionDetail = lazy(() => import('./components/QuestionDetail'));
const CreateBattle = lazy(() => import('./components/CreateBattle'));
const BattleRoom = lazy(() => import('./components/BattleRoom'));
const JoinBattle = lazy(() => import('./components/JoinBattle'));
const BattleHistory = lazy(() => import('./components/BattleHistory'));
const Settings = lazy(() => import('./components/Settings'));
const AdminDashboard = lazy(() => import('./components/AdminDashboard'));
const AdminUsers = lazy(() => import('./components/AdminUsers'));
const AdminQuestions = lazy(() => import('./components/AdminQuestions'));
const AdminLogs = lazy(() => import('./components/AdminLogs'));
const AdminReports = lazy(() => import('./components/AdminReports'));

const LoadingScreen = () => (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" aria-label="Loading" />
    </div>
);

function App() {
    return (
        <AuthProvider>
            <Router>
                <div className="min-h-screen bg-white">
                    <Suspense fallback={<LoadingScreen />}>
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
                    </Suspense>
                </div>
            </Router>
        </AuthProvider>
    );
}

export default App;
