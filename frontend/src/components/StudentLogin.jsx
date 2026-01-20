import React, { useState } from 'react';
import { User, ArrowRight } from 'lucide-react';
import { authService } from '../services/authService';

const StudentLogin = ({ onLogin }) => {
    const [name, setName] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!name.trim()) return;

        setLoading(true);
        try {
            const student = await studyService.loginStudent(name);
            onLogin(student); // {id, name}
        } catch (err) {
            console.error(err);
            alert("Erro ao entrar. Tenta novamente.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6 relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 left-0 w-full h-full opacity-5 pointer-events-none">
                <div className="absolute top-10 left-10 w-32 h-32 bg-duo-green rounded-full blur-3xl"></div>
                <div className="absolute bottom-10 right-10 w-48 h-48 bg-duo-blue rounded-full blur-3xl"></div>
            </div>

            <div className="max-w-md w-full animate-fade-in text-center relative z-10">
                <div className="w-32 h-32 mx-auto mb-8 relative">
                    <div className="absolute inset-0 bg-duo-green rounded-3xl rotate-6 opacity-20"></div>
                    <div className="absolute inset-0 bg-duo-blue rounded-3xl -rotate-6 opacity-20"></div>
                    <div className="relative bg-white border-4 border-gray-100 rounded-3xl w-full h-full flex items-center justify-center shadow-sm">
                        <span className="text-6xl">🎓</span>
                    </div>
                </div>

                <h1 className="text-3xl font-bold text-gray-700 mb-2 tracking-tight">Vamos aprender!</h1>
                <p className="text-gray-400 font-bold uppercase text-sm tracking-wide mb-10">Entra para começar</p>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="Como te chamas?"
                        className="w-full text-center text-xl font-bold p-4 bg-gray-50 border-2 border-gray-200 border-b-4 rounded-2xl focus:border-duo-blue focus:bg-white placeholder-gray-300 transition-all outline-none text-gray-700"
                        autoFocus
                    />

                    <button
                        type="submit"
                        disabled={loading || !name.trim()}
                        className="w-full bg-duo-green border-b-4 border-duo-green-dark hover:bg-[#61E002] active:border-b-0 active:translate-y-1 text-white font-bold py-4 rounded-2xl uppercase tracking-wider transition-all flex items-center justify-center gap-2 text-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:border-gray-200 disabled:bg-gray-100 disabled:text-gray-300"
                    >
                        {loading ? 'A entrar...' : 'CONTINUAR'}
                    </button>
                </form>
            </div>
        </div>
    );
};

export default StudentLogin;
