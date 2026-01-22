import React, { useState } from 'react';
import { Eye, EyeOff, User, Lock, Sparkles, GraduationCap, ArrowRight, Rocket } from 'lucide-react';
import { authService } from '../services/authService';
import mascotImg from '../assets/mascot.png';

const LoginPage = ({ onLogin }) => {
    const [isRegistering, setIsRegistering] = useState(false);
    const [name, setName] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // Frontend validation
    const isFormValid = () => {
        if (name.trim().length < 2) return false;

        // Backend Policy: 8+ chars, 1 upper, 1 lower, 1 digit, 1 special
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSpecial = /[@$!%*?&]/.test(password);

        if (password.length < 8) return false;
        if (!hasUpper || !hasLower || !hasDigit || !hasSpecial) return false;

        if (isRegistering && password !== confirmPassword) return false;
        return true;
    };

    const handleAction = async (e) => {
        e.preventDefault();
        setError("");

        // Validate
        if (name.trim().length < 2) {
            setError("O nome deve ter pelo menos 2 caracteres.");
            return;
        }

        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasDigit = /\d/.test(password);
        const hasSpecial = /[@$!%*?&]/.test(password);

        if (password.length < 8 || !hasUpper || !hasLower || !hasDigit || !hasSpecial) {
            setError("A password deve ter 8+ caracteres, maiúscula, minúscula, número e símbolo (@$!%*?&).");
            return;
        }
        if (isRegistering && password !== confirmPassword) {
            setError("As palavras-passe não coincidem.");
            return;
        }

        setLoading(true);

        try {
            let student;
            if (isRegistering) {
                student = await authService.registerStudent(name, password);
            } else {
                student = await authService.loginStudent(name, password);
            }
            // Clear password from state after successful login (security)
            setPassword("");
            setConfirmPassword("");
            onLogin(student);
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.detail || "Ocorreu um erro. Verifica a tua ligação.";
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-500 to-indigo-700 flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans">

            {/* Animated Background Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {/* Subtle Grid Pattern */}
                <div className="absolute inset-0 opacity-10"
                    style={{ backgroundImage: 'radial-gradient(#fff 2px, transparent 2px)', backgroundSize: '30px 30px' }}>
                </div>

                {/* Floating Orbs */}
                <div className="absolute top-20 left-10 w-40 h-40 bg-white rounded-full blur-3xl opacity-20 animate-pulse"></div>
                <div className="absolute bottom-20 right-10 w-60 h-60 bg-purple-400 rounded-full blur-3xl opacity-30 animate-pulse" style={{ animationDelay: '1s' }}></div>
                <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-yellow-300 rounded-full blur-xl opacity-20 animate-bounce-slow"></div>
            </div>

            <div className="max-w-md w-full animate-scale-in relative z-10">

                {/* Brand / Mascot Area */}
                <div className="text-center mb-8">
                    <div className="inline-block relative">
                        <div className="absolute inset-0 bg-blue-500 rounded-full blur-2xl opacity-30 animate-pulse"></div>
                        <div className="relative bg-white p-2 rounded-[2rem] shadow-xl border-b-8 border-gray-200 transform hover:scale-105 transition-transform duration-300">
                            {/* mix-blend-multiply hides the white background of the image against the white card */}
                            <img src={mascotImg} alt="Mascote Super Study" className="w-32 h-32 object-contain mix-blend-multiply" />
                        </div>
                        <div className="absolute -top-4 -right-4 bg-yellow-400 text-yellow-900 font-black text-xs px-3 py-1 rounded-full uppercase tracking-widest border-2 border-yellow-500 transform rotate-12 animate-bounce-short">
                            Novo!
                        </div>
                    </div>
                    <h1 className="text-4xl font-black text-white mt-6 mb-2 tracking-tight">
                        Super Study! <Rocket className="inline-block ml-2 text-yellow-400 animate-bounce-slow" size={32} />
                    </h1>
                    <p className="text-blue-200 font-bold uppercase tracking-widest text-sm">
                        Torna o estudo na tua aventura favorita!
                    </p>
                </div>

                {/* Main Card */}
                <div className="bg-white rounded-[2.5rem] p-8 shadow-2xl border-b-8 border-blue-900/10">

                    <h2 className="text-2xl font-black text-gray-800 mb-6 text-center">
                        {isRegistering ? "Junta-te a nós! É grátis!" : "Olá de novo, campeão!"}
                    </h2>

                    {error && (
                        <div className="bg-red-50 border-2 border-red-100 text-red-500 p-4 rounded-2xl mb-6 text-sm font-bold animate-shake text-center">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleAction} className="space-y-4">
                        {/* Name Input */}
                        <div className="relative group">
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 transition-colors">
                                <User size={24} strokeWidth={2.5} />
                            </div>
                            <input
                                type="text"
                                aria-label="Nome de super-herói"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Qual é o teu nome de super-herói?"
                                className="w-full pl-14 pr-4 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl outline-none font-bold text-gray-700 placeholder-gray-400 focus:border-blue-500 focus:bg-white transition-all text-lg"
                                autoFocus={!isRegistering}
                            />
                        </div>

                        {/* Password Input */}
                        <div className="relative group">
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-blue-500 transition-colors">
                                <Lock size={24} strokeWidth={2.5} />
                            </div>
                            <input
                                type={showPassword ? "text" : "password"}
                                aria-label="Palavra-passe"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="A tua palavra-passe secreta"
                                className="w-full pl-14 pr-14 py-4 bg-gray-50 border-2 border-gray-200 rounded-2xl outline-none font-bold text-gray-700 placeholder-gray-400 focus:border-blue-500 focus:bg-white transition-all text-lg"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 p-1"
                            >
                                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                            </button>
                        </div>

                        {/* Confirm Password Input (Registration Only) */}
                        {isRegistering && (
                            <div className="relative group">
                                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-green-500 transition-colors">
                                    <Lock size={24} strokeWidth={2.5} />
                                </div>
                                <input
                                    type={showPassword ? "text" : "password"}
                                    aria-label="Confirmar palavra-passe"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    placeholder="Confirma a palavra-passe"
                                    className={`w-full pl-14 pr-4 py-4 bg-gray-50 border-2 rounded-2xl outline-none font-bold text-gray-700 placeholder-gray-400 focus:bg-white transition-all text-lg ${confirmPassword && password !== confirmPassword
                                        ? 'border-red-300 focus:border-red-500'
                                        : 'border-gray-200 focus:border-green-500'
                                        }`}
                                />
                            </div>
                        )}

                        {/* Inline Validation Hints */}
                        {(name.length > 0 || password.length > 0 || confirmPassword.length > 0) && !isFormValid() && (
                            <div className="text-sm font-bold text-orange-500 text-center py-2 px-4 bg-orange-50 rounded-xl border border-orange-100 flex flex-col gap-1">
                                {name.trim().length > 0 && name.trim().length < 2 && <span>Nome curto demais (mín. 2).</span>}
                                {password.length > 0 && (
                                    <>
                                        {password.length < 8 && <span>Mín. 8 caracteres.</span>}
                                        {!/[A-Z]/.test(password) && <span>Falta maiúscula.</span>}
                                        {!/[a-z]/.test(password) && <span>Falta minúscula.</span>}
                                        {!/\d/.test(password) && <span>Falta número.</span>}
                                        {!/[@$!%*?&]/.test(password) && <span>Falta símbolo.</span>}
                                    </>
                                )}
                                {isRegistering && confirmPassword.length > 0 && password !== confirmPassword && <span>Palavras-passe não coincidem.</span>}
                            </div>
                        )}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading || !isFormValid()}
                            className={`w-full py-4 rounded-2xl border-b-[6px] font-black text-white uppercase tracking-widest text-lg transition-all active:border-b-0 active:translate-y-[6px] flex items-center justify-center gap-2 shadow-lg ${loading || !isFormValid()
                                ? 'opacity-50 cursor-not-allowed bg-gray-400 border-gray-500'
                                : isRegistering
                                    ? 'bg-green-500 border-green-700 hover:bg-green-400'
                                    : 'bg-blue-500 border-blue-700 hover:bg-blue-400'
                                }`}
                        >
                            {loading ? (
                                <span className="animate-pulse">A carregar...</span>
                            ) : (
                                <>
                                    {isRegistering ? 'COMEÇAR A AVENTURA' : 'CONTINUAR A JORNADA'}
                                    <ArrowRight size={24} strokeWidth={3} />
                                </>
                            )}
                        </button>
                    </form>
                </div>

                {/* Toggle Mode */}
                <div className="mt-8 text-center">
                    <button
                        onClick={() => {
                            setIsRegistering(!isRegistering);
                            setError("");
                            setName("");
                            setPassword("");
                            setConfirmPassword("");
                        }}
                        className="text-white/80 font-bold uppercase tracking-wider text-sm hover:text-white hover:underline transition-all"
                    >
                        {isRegistering
                            ? "JÁ FAZES PARTE DA EQUIPA? ENTRAR"
                            : "AINDA NÃO TENS CONTA? CRIA UMA GRÁTIS"}
                    </button>
                </div>
            </div>

            {/* Version */}
            <div className="absolute bottom-4 text-slate-800 font-bold text-xs uppercase tracking-widest opacity-40">
                v2.1 • Super Study
            </div>
        </div>
    );
};

export default LoginPage;
