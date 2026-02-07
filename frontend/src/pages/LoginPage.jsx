import { useState } from 'react';
import { Eye, EyeOff, User, Lock, ArrowRight, Shield, Key } from 'lucide-react';
import { authService } from '../services/authService';
import mascotImg from '../assets/mascot.png';

const LoginPage = ({ onLogin }) => {
    const [isRegistering, setIsRegistering] = useState(false);
    const [name, setName] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [inviteCode, setInviteCode] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const registerEnabled = String(import.meta.env.VITE_REGISTER_ENABLED || "true").toLowerCase() !== "false";

    // Frontend validation
    const isFormValid = () => {
        if (name.trim().length < 2) return false;

        if (isRegistering) {
            if (!registerEnabled) return false;
            // Backend Policy: 8+ chars, 1 upper, 1 lower, 1 digit, 1 special
            const hasUpper = /[A-Z]/.test(password);
            const hasLower = /[a-z]/.test(password);
            const hasDigit = /\d/.test(password);
            const hasSpecial = /[@$!%*?&]/.test(password);

            if (password.length < 8) return false;
            if (!hasUpper || !hasLower || !hasDigit || !hasSpecial) return false;
            if (password !== confirmPassword) return false;
            if (inviteCode.trim().length === 0) return false;
        } else {
            // Login: Just needs to be filled
            if (password.length === 0) return false;
        }

        return true;
    };

    const handleAction = async (e) => {
        e.preventDefault();
        setError("");

        // Validate
        if (name.trim().length < 2) {
            setError("O nome de agente deve ter pelo menos 2 caracteres.");
            return;
        }

        if (isRegistering) {
            if (!registerEnabled) {
                setError("Registo desativado.");
                return;
            }
            const hasUpper = /[A-Z]/.test(password);
            const hasLower = /[a-z]/.test(password);
            const hasDigit = /\d/.test(password);
            const hasSpecial = /[@$!%*?&]/.test(password);

            if (password.length < 8 || !hasUpper || !hasLower || !hasDigit || !hasSpecial) {
                setError("A credencial deve ter 8+ caracteres, maiúscula, minúscula, número e símbolo (@$!%*?&).");
                return;
            }
            if (password !== confirmPassword) {
                setError("As credenciais não coincidem.");
                return;
            }
            if (inviteCode.trim().length === 0) {
                setError("Codigo de convite obrigatorio.");
                return;
            }
        }

        setLoading(true);

        try {
            let student;
            if (isRegistering) {
                student = await authService.registerStudent(name, password, inviteCode.trim());
            } else {
                student = await authService.loginStudent(name, password);
            }
            // Clear password from state after successful login (security)
            setPassword("");
            setConfirmPassword("");
            setInviteCode("");
            onLogin(student);
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.detail || "Erro de ligação ao servidor central.";
            setError(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-900 flex flex-col items-center justify-center p-6 relative overflow-hidden font-sans selection:bg-yellow-400 selection:text-black">

            {/* Premium Background Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute inset-0 opacity-[0.03]"
                    style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)', backgroundSize: '40px 40px' }}>
                </div>
                <div className="absolute top-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px]"></div>
                <div className="absolute bottom-[-10%] left-[-10%] w-[500px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px]"></div>
            </div>

            <div className="max-w-md w-full animate-scale-in relative z-10">

                {/* Brand / Mascot Area */}
                <div className="text-center mb-10">
                    <div className="inline-block relative group">
                        <div className="absolute inset-0 bg-yellow-400 rounded-full blur-xl opacity-20 group-hover:opacity-40 transition-opacity duration-500"></div>
                        <div className="relative bg-gray-800 p-4 rounded-3xl shadow-2xl border border-gray-700 transform group-hover:scale-105 transition-transform duration-300">
                            <img src={mascotImg} alt="Mascote Super Study" className="w-24 h-24 object-contain mix-blend-multiply filter contrast-125" />
                        </div>
                    </div>
                    <h1 className="text-3xl font-black text-white mt-6 mb-2 tracking-tight">
                        Super Study <span className="text-yellow-400">HQ</span>
                    </h1>
                    <p className="text-gray-400 font-medium text-sm">
                        Plataforma de Operações de Estudo v2.0
                        </p>
                </div>

                {/* Main Card */}
                <div className="bg-gray-800/50 backdrop-blur-xl rounded-[2rem] p-8 shadow-2xl border border-white/10 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-blue-500 to-transparent opacity-50"></div>

                    <h2 className="text-xl font-bold text-white mb-8 flex items-center gap-3">
                        {isRegistering ? (
                            <>
                                <div className="p-2 bg-green-500/10 rounded-lg text-green-400"><User size={20} /></div>
                                Novo Recruta
                            </>
                        ) : (
                            <>
                                <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400"><Key size={20} /></div>
                                Acesso de Agente
                            </>
                        )}
                    </h2>

                    {error && (
                        <div className="bg-red-500/10 border border-red-500/20 text-red-200 p-4 rounded-xl mb-6 text-sm font-medium animate-shake flex items-center gap-3">
                            <Shield size={16} className="shrink-0" />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleAction} className="space-y-5">
                        {/* Name Input */}
                        <div className="relative group">
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-yellow-400 transition-colors">
                                <User size={20} />
                            </div>
                            <input
                                type="text"
                                aria-label="Nome de Agente"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="Codename do Agente"
                                className="w-full pl-12 pr-4 py-4 bg-gray-900/50 border border-gray-700 rounded-xl outline-none font-bold text-white placeholder-gray-600 focus:border-yellow-400/50 focus:bg-gray-900 transition-all text-sm"
                                autoFocus={!isRegistering}
                            />
                        </div>

                        {/* Password Input */}
                        <div className="relative group">
                            <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-yellow-400 transition-colors">
                                <Lock size={20} />
                            </div>
                            <input
                                type={showPassword ? "text" : "password"}
                                aria-label="Chave de Acesso"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Chave de Acesso"
                                className="w-full pl-12 pr-12 py-4 bg-gray-900/50 border border-gray-700 rounded-xl outline-none font-bold text-white placeholder-gray-600 focus:border-yellow-400/50 focus:bg-gray-900 transition-all text-sm"
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-600 hover:text-white p-1 transition-colors"
                            >
                                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>

                        {/* Confirm Password Input (Registration Only) */}
                        {isRegistering && (
                            <div className="relative group animate-slide-down">
                                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-green-400 transition-colors">
                                    <Shield size={20} />
                                </div>
                                <input
                                    type={showPassword ? "text" : "password"}
                                    aria-label="Confirmar Chave"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    placeholder="Confirmar Chave de Acesso"
                                    className={`w-full pl-12 pr-4 py-4 bg-gray-900/50 border rounded-xl outline-none font-bold text-white placeholder-gray-600 focus:bg-gray-900 transition-all text-sm ${confirmPassword && password !== confirmPassword
                                        ? 'border-red-500/50 focus:border-red-500'
                                        : 'border-gray-700 focus:border-green-500/50'
                                        }`}
                                />
                            </div>
                        )}

                        {/* Invite Code Input (Registration Only) */}
                        {isRegistering && (
                            <div className="relative group animate-slide-down">
                                <div className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 group-focus-within:text-yellow-400 transition-colors">
                                    <Key size={20} />
                                </div>
                                <input
                                    type="text"
                                    aria-label="Codigo de Convite"
                                    value={inviteCode}
                                    onChange={(e) => setInviteCode(e.target.value)}
                                    placeholder="Codigo de Convite"
                                    className="w-full pl-12 pr-4 py-4 bg-gray-900/50 border border-gray-700 rounded-xl outline-none font-bold text-white placeholder-gray-600 focus:border-yellow-400/50 focus:bg-gray-900 transition-all text-sm"
                                />
                            </div>
                        )}

                        {/* Validation Hints (Cleaner) */}
                        {(() => {
                            const errors = [];
                            if (isRegistering && password.length > 0) {
                                if (password.length < 8) errors.push(<span key="len" className="text-red-400">• Mín. 8 chars</span>);
                                if (!/[A-Z]/.test(password)) errors.push(<span key="upper" className="text-red-400">• Maiúscula</span>);
                                if (!/[a-z]/.test(password)) errors.push(<span key="lower" className="text-red-400">• Minúscula</span>);
                                if (!/\d/.test(password)) errors.push(<span key="digit" className="text-red-400">• Número</span>);
                                if (!/[@$!%*?&]/.test(password)) errors.push(<span key="special" className="text-red-400">• Símbolo</span>);
                            }

                            if (errors.length === 0) return null;

                            return (
                                <div className="text-xs font-medium text-gray-400 flex flex-wrap gap-2 px-2">
                                    {errors}
                                </div>
                            );
                        })()}

                        {/* Submit Button */}
                        <button
                            type="submit"
                            disabled={loading || !isFormValid()}
                            className={`w-full py-4 rounded-xl font-black text-black uppercase tracking-widest text-sm transition-all flex items-center justify-center gap-2 ${loading || !isFormValid()
                                ? 'opacity-50 cursor-not-allowed bg-gray-700 text-gray-500'
                                : 'bg-yellow-400 hover:bg-yellow-300 hover:shadow-[0_0_20px_rgba(250,204,21,0.4)] active:scale-[0.98]'
                                }`}
                        >
                            {loading ? (
                                <span className="animate-pulse">A desencriptar...</span>
                            ) : (
                                <>
                                    {isRegistering ? 'INICIAR RECRUTAMENTO' : 'ACEDER AO SISTEMA'}
                                    <ArrowRight size={18} strokeWidth={3} />
                                </>
                            )}
                        </button>
                    </form>
                </div>

                {/* Toggle Mode */}
                {registerEnabled && (
                    <div className="mt-8 text-center space-y-2">
                        <p className="text-gray-500 text-xs">
                            {isRegistering ? "J? tens credenciais?" : "Ainda n?o tens acesso?"}
                        </p>
                        <button
                            onClick={() => {
                                setIsRegistering(!isRegistering);
                                setError("");
                                setName("");
                                setPassword("");
                                setConfirmPassword("");
                                setInviteCode("");
                            }}
                            className="text-white font-bold uppercase tracking-wider text-xs hover:text-yellow-400 hover:underline transition-all"
                        >
                            {isRegistering
                                ? "LOGIN DE AGENTE"
                                : "SOLICITAR ACESSO"}
                        </button>
                    </div>
                )}
            </div>

            {/* Version */}
            <div className="absolute bottom-6 font-mono text-gray-800 text-[10px] uppercase tracking-widest">
                System v2.1 • Secure Connection
            </div>
        </div>
    );
};

export default LoginPage;
