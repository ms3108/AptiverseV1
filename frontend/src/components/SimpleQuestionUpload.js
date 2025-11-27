import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import API_URL from '../config/api';

const SimpleQuestionUpload = () => {
    const { token } = useAuth();
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setResult(null);
    };

    const handleUpload = async (e) => {
        e.preventDefault();
        
        if (!file) {
            alert('Please select a file');
            return;
        }

        setUploading(true);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post(`${API_URL}/admin/questions/upload`, formData, {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'multipart/form-data'
                }
            });

            setResult({
                success: true,
                data: response.data
            });
            setFile(null);
            
        } catch (error) {
            console.error('Upload failed:', error);
            setResult({
                success: false,
                error: error.response?.data?.detail || 'Upload failed'
            });
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow">
            <h2 className="text-2xl font-bold mb-6">Upload Questions</h2>
            
            {/* Format Guide */}
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                <h3 className="font-semibold mb-2">Required JSON Format:</h3>
                <pre className="text-sm bg-gray-100 p-3 rounded overflow-x-auto">
{`[
  {
    "title": "Question Title",
    "description": "Question text here",
    "difficulty": "Hard",
    "topic": "Synonyms",
    "option_a": "Option A",
    "option_b": "Option B", 
    "option_c": "Option C",
    "option_d": "Option D",
    "correct_answer": "B",
    "explanation": "Explanation here",
    "xp_reward": 20
  }
]`}
                </pre>
                <p className="text-sm text-gray-600 mt-2">
                    <strong>Required:</strong> title, description, difficulty (Easy/Medium/Hard), topic, 
                    option_a, option_b, option_c, option_d, correct_answer (A/B/C/D), explanation, xp_reward
                </p>
            </div>

            {/* Upload Form */}
            <form onSubmit={handleUpload} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium mb-2">
                        Select JSON File
                    </label>
                    <input
                        type="file"
                        accept=".json"
                        onChange={handleFileChange}
                        className="block w-full text-sm text-gray-500
                                 file:mr-4 file:py-2 file:px-4
                                 file:rounded file:border-0
                                 file:text-sm file:font-semibold
                                 file:bg-blue-50 file:text-blue-700
                                 hover:file:bg-blue-100"
                    />
                </div>

                <button
                    type="submit"
                    disabled={!file || uploading}
                    className="w-full py-2 px-4 bg-blue-600 text-white rounded
                             hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {uploading ? 'Uploading...' : 'Upload Questions'}
                </button>
            </form>

            {/* Results */}
            {result && (
                <div className={`mt-6 p-4 rounded-lg ${result.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                    {result.success ? (
                        <div>
                            <h3 className="font-semibold text-green-800 mb-2">Upload Successful!</h3>
                            <div className="text-sm text-green-700">
                                <p>Total in file: {result.data.stats.total_in_file}</p>
                                <p>Successfully added: {result.data.stats.added}</p>
                                {result.data.stats.errors_count > 0 && (
                                    <p>Errors: {result.data.stats.errors_count}</p>
                                )}
                            </div>
                            {result.data.errors && result.data.errors.length > 0 && (
                                <div className="mt-2">
                                    <p className="font-medium text-red-600">Errors:</p>
                                    <ul className="text-sm text-red-700 list-disc list-inside">
                                        {result.data.errors.map((error, idx) => (
                                            <li key={idx}>{error}</li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div>
                            <h3 className="font-semibold text-red-800 mb-2">Upload Failed</h3>
                            <p className="text-sm text-red-700">{result.error}</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default SimpleQuestionUpload;