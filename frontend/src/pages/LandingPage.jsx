import { Rocket, Brain, Zap, ArrowRight, CheckCircle, Shield, FileText } from 'lucide-react';
import mascotImg from '../assets/mascot.png';

const LandingPage = ({ onStart }) => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-blue-800 to-indigo-900 font-sans text-white overflow-x-hidden selection:bg-yellow-400 selection:text-indigo-900">

            {/* Nav */}
            <nav className="max-w-7xl mx-auto px-6 py-6 flex justify-between items-center relative z-20">
                <div className="flex items-center gap-2">
                    <div className="bg-white p-2 rounded-xl shadow-[0_0_20px_rgba(255,255,255,0.2)] rotate-3 active:rotate-0 transition-transform cursor-pointer">
                        <img src={mascotImg} alt="Super Study Logo" className="w-8 h-8 object-contain mix-blend-multiply" />
                    </div>
                    <span className="font-black text-2xl tracking-tight text-white drop-shadow-lg">Super Study</span>
                </div>
                <div className="flex items-center gap-4">
                    <button
                        onClick={onStart}
                        className="font-bold text-blue-200 hover:text-white px-4 py-2 rounded-xl transition-all hidden md:block"
                    >
                        Login
                    </button>
                    <button
                        onClick={onStart}
                        className="bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 font-bold text-white px-6 py-2 rounded-xl transition-all shadow-lg hover:shadow-xl active:scale-95"
                    >
                        Começar Agora
                    </button>
                </div>
            </nav>

            {/* Hero Section (Dual Audience: Fun for Kids, Results for Parents) */}
            <div className="max-w-7xl mx-auto px-6 pt-12 pb-20 lg:pt-20 grid lg:grid-cols-2 gap-12 items-center relative z-10">
                <div className="space-y-8 animate-slide-in-left">
                    <div className="inline-flex items-center gap-2 bg-yellow-400/10 border border-yellow-400/30 text-yellow-300 font-bold text-xs px-4 py-1.5 rounded-full uppercase tracking-widest backdrop-blur-sm">
                        <Zap size={14} className="fill-current" />
                        <span>A Nova Meta do Estudo</span>
                    </div>

                    <h1 className="text-5xl lg:text-7xl font-black leading-[1.1] tracking-tight">
                        O explicador IA que torna o estudo <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-300 to-yellow-500 underline decoration-wavy decoration-yellow-400/30 underline-offset-8">viciante</span>.
                    </h1>

                    <p className="text-blue-100 text-lg lg:text-xl font-medium leading-relaxed max-w-xl">
                        Para o <span className="text-white font-bold">Aluno</span>: Menos seca, mais XP. <br className="hidden md:block" />
                        Para os <span className="text-white font-bold">Pais</span>: Melhores notas, zero discussões.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 pt-4">
                        <button
                            onClick={onStart}
                            className="bg-yellow-400 text-yellow-900 px-8 py-4 rounded-2xl font-black text-lg shadow-[0_4px_0_rgb(161,98,7)] hover:shadow-[0_2px_0_rgb(161,98,7)] hover:translate-y-[2px] active:translate-y-[4px] active:shadow-none transition-all flex items-center justify-center gap-3 uppercase tracking-wide group"
                        >
                            Começar Grátis
                            <ArrowRight className="group-hover:translate-x-1 transition-transform" strokeWidth={3} />
                        </button>
                        <p className="text-blue-300/60 text-xs font-bold uppercase tracking-widest text-center sm:text-left mt-2 sm:mt-0 flex items-center justify-center sm:justify-start gap-2">
                            <Shield size={14} /> Sem cartão de crédito
                        </p>
                    </div>

                    {/* Social Proof (Trust Builders) */}
                    <div className="pt-8 border-t border-white/10">
                        <p className="text-blue-200/60 text-xs font-bold uppercase tracking-widest mb-4">Usado por estudantes de elite em:</p>
                        <div className="flex gap-6 opacity-50 grayscale hover:grayscale-0 transition-all duration-500">
                            {/* University Logos Placeholders - Replace with SVGs */}
                            <div className="h-8 w-24 bg-white/20 rounded flex items-center justify-center text-[10px] font-black">IST</div>
                            <div className="h-8 w-24 bg-white/20 rounded flex items-center justify-center text-[10px] font-black">FEUP</div>
                            <div className="h-8 w-24 bg-white/20 rounded flex items-center justify-center text-[10px] font-black">FDUC</div>
                            <div className="h-8 w-24 bg-white/20 rounded flex items-center justify-center text-[10px] font-black hidden md:flex">NOVA</div>
                        </div>
                    </div>
                </div>

                {/* Visual Demo (The "Ghost Product" Fix) */}
                <div className="relative lg:h-[600px] flex items-center justify-center perspective-1000">
                    {/* Background Glow */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[140%] h-[140%] bg-blue-500/20 rounded-full blur-[100px]"></div>

                    {/* The "Machine" */}
                    <div className="relative w-full max-w-md bg-gradient-to-b from-gray-900 to-black rounded-[2.5rem] p-4 shadow-2xl border border-white/10 transform rotate-y-[-10deg] hover:rotate-y-0 transition-transform duration-700 ease-out-expo">
                        {/* Fake UI Header */}
                        <div className="absolute top-0 left-0 w-full h-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none"></div>

                        <div className="bg-gray-800/50 rounded-[2rem] p-6 backdrop-blur-xl relative overflow-hidden h-[500px] flex flex-col">
                            {/* Step 1: Upload */}
                            <div className="flex items-center gap-3 mb-6 bg-white/5 p-3 rounded-xl border border-white/10 animate-pulse-slow">
                                <div className="bg-red-500/20 p-2 rounded-lg text-red-400">
                                    <FileText size={20} />
                                </div>
                                <div>
                                    <p className="text-xs text-gray-400 font-mono">biologia_12ano.pdf</p>
                                    <div className="w-32 h-1.5 bg-gray-700 rounded-full mt-1 overflow-hidden">
                                        <div className="w-full h-full bg-green-400 animate-progress"></div>
                                    </div>
                                </div>
                                <CheckCircle size={16} className="text-green-400 ml-auto" />
                            </div>

                            {/* Arrow Down */}
                            <div className="flex justify-center mb-6">
                                <div className="bg-gray-900 border border-gray-700 p-2 rounded-full animate-bounce">
                                    <ArrowRight className="rotate-90 text-yellow-400" size={20} />
                                </div>
                            </div>

                            {/* Step 2: Quiz Gen */}
                            <div className="flex-1 bg-white rounded-2xl p-4 shadow-lg transform translate-y-2 relative border-b-4 border-gray-200">
                                <div className="absolute -top-3 -right-3 bg-yellow-400 text-yellow-900 text-xs font-black px-2 py-1 rounded badge-pulse">
                                    +50 XP
                                </div>
                                <div className="flex gap-2 items-center mb-4">
                                    <span className="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-1 rounded-md">BIOLOGIA</span>
                                    <span className="text-gray-400 text-[10px] font-bold">Q. 1/15</span>
                                </div>
                                <p className="text-gray-800 font-bold text-sm mb-4">O que define a mitose?</p>
                                <div className="space-y-2">
                                    <div className="p-3 rounded-xl bg-gray-50 border-2 border-transparent hover:border-blue-400 text-xs font-medium text-gray-600 cursor-pointer">
                                        Divisão celular redutora...
                                    </div>
                                    <div className="p-3 rounded-xl bg-green-100 border-2 border-green-500 text-xs font-bold text-green-900 cursor-pointer flex justify-between items-center shadow-sm">
                                        Divisão celular equacional...
                                        <CheckCircle size={14} />
                                    </div>
                                    <div className="p-3 rounded-xl bg-gray-50 border-2 border-transparent hover:border-blue-400 text-xs font-medium text-gray-600 cursor-pointer">
                                        Fusão de gâmetas...
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Floating Mascot */}
                        <img src={mascotImg} alt="Mascot" className="absolute -bottom-10 -right-10 w-40 h-40 mix-blend-multiply drop-shadow-2xl animate-float pointer-events-none" />
                    </div>
                </div>
            </div>

            {/* Value Props Section (Translated for Both Audiences) */}
            <div className="py-24 bg-gray-900 px-6 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent"></div>

                <div className="max-w-6xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-black text-white mb-6">Um cérebro novo em 3 passos.</h2>
                        <p className="text-gray-400 text-lg">Tu ganhas tempo. Eles ganham tranquilidade.</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {/* Card 1: Processing */}
                        <FeatureCard
                            icon={<Brain size={32} className="text-purple-400" />}
                            title="Triturador de Matéria"
                            studentBenefit="Tu carregas o PDF de 50 páginas. A IA resume só o que importa em segundos."
                            parentBenefit="Poupas em explicadores. O estudo torna-se focado e eficiente."
                            bg="bg-purple-500/10"
                            border="border-purple-500/20"
                        />
                        {/* Card 2: Simulation */}
                        <FeatureCard
                            icon={<TargetIcon />}
                            title="Simulador de Exame"
                            studentBenefit="Treina com perguntas iguais às do teste. Sem surpresas."
                            parentBenefit="Acaba com a ansiedade pré-teste. O teu filho vai preparado."
                            bg="bg-pink-500/10"
                            border="border-pink-500/20"
                        />
                        {/* Card 3: Gamification */}
                        <FeatureCard
                            icon={<TrophyIcon />}
                            title="Gamificação Hardcore"
                            studentBenefit="Sobe de nível, ganha skins e compete nas leaderboards."
                            parentBenefit="O único 'jogo' que melhora as notas. Vício produtivo."
                            bg="bg-yellow-500/10"
                            border="border-yellow-500/20"
                        />
                    </div>
                </div>
            </div>

            {/* Parents Only Section (Trust & Safety) */}
            <div className="bg-white py-24 px-6 relative">
                <div className="max-w-5xl mx-auto">
                    <div className="flex flex-col md:flex-row items-center gap-12">
                        <div className="w-full md:w-1/2 relative">
                            <div className="absolute inset-0 bg-blue-100 rounded-full blur-3xl opacity-50"></div>
                            <div className="relative bg-white border border-gray-100 shadow-2xl rounded-3xl p-8">
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center text-green-600">
                                        <Shield size={24} />
                                    </div>
                                    <div>
                                        <h4 className="font-black text-gray-800 text-lg">Modo Anti-Alucinação</h4>
                                        <p className="text-xs text-gray-500 font-bold uppercase tracking-wider">Segurança Ativa</p>
                                    </div>
                                </div>
                                <div className="space-y-4">
                                    <div className="flex gap-3 text-sm text-gray-600">
                                        <CheckCircle size={18} className="text-green-500 shrink-0" />
                                        <p>A IA baseia-se <strong>apenas</strong> nos documentos carregados.</p>
                                    </div>
                                    <div className="flex gap-3 text-sm text-gray-600">
                                        <CheckCircle size={18} className="text-green-500 shrink-0" />
                                        <p>Conteúdo filtrado e apropriado para menores.</p>
                                    </div>
                                    <div className="flex gap-3 text-sm text-gray-600">
                                        <CheckCircle size={18} className="text-green-500 shrink-0" />
                                        <p>Relatórios de progresso semanais.</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="w-full md:w-1/2 space-y-6">
                            <div className="inline-block bg-blue-100 text-blue-800 font-bold text-xs px-3 py-1 rounded-full uppercase tracking-widest">
                                Para os Pais
                            </div>
                            <h2 className="text-4xl font-black text-gray-900 leading-tight">
                                Transforme o &quot;Tempo de Ecrã&quot; em <span className="text-blue-600">Tempo de Estudo</span>.
                            </h2>
                            <p className="text-gray-600 text-lg leading-relaxed">
                                Sabemos que a batalha contra o telemóvel é difícil. O Super Study usa a mesma psicologia viciante dos videojogos para criar hábitos de estudo consistentes.
                            </p>
                            <p className="text-gray-600 text-lg leading-relaxed">
                                O seu filho estuda autonomamente, e ganha a paz de espírito de saber que ele está a aprender de verdade.
                            </p>
                            <button
                                onClick={onStart}
                                className="text-blue-600 font-black flex items-center gap-2 hover:gap-4 transition-all"
                            >
                                Experimentar sem compromisso <ArrowRight strokeWidth={3} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Final CTA */}
            <div className="bg-indigo-900 py-24 px-6 relative overflow-hidden text-center">
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10"></div>
                <div className="relative z-10 max-w-3xl mx-auto">
                    <h2 className="text-4xl md:text-6xl font-black text-white mb-8 tracking-tight">
                        A tua nota de sonho espera por ti.
                    </h2>
                    <p className="text-blue-200 text-xl font-medium mb-10 max-w-2xl mx-auto">
                        Junta-te a milhares de estudantes que deixaram de estudar até às 4 da manhã.
                    </p>
                    <button
                        onClick={onStart}
                        className="bg-yellow-400 text-yellow-900 px-12 py-6 rounded-2xl font-black text-2xl shadow-[0_6px_0_rgb(161,98,7)] hover:shadow-[0_4px_0_rgb(161,98,7)] hover:translate-y-[2px] active:translate-y-[4px] active:shadow-none transition-all inline-flex items-center gap-4 hover:scale-105 duration-300"
                    >
                        <Rocket size={32} />
                        COMEÇAR AGORA
                    </button>
                    <p className="mt-6 text-white/40 text-sm font-bold uppercase tracking-widest">
                        Totalmente Grátis para começar
                    </p>
                </div>
            </div>

            {/* Simple Footer */}
            <footer className="bg-black py-12 border-t border-white/10 text-center text-white/20 text-sm font-bold uppercase tracking-widest">
                &copy; {new Date().getFullYear()} Super Study. Made for Students.
            </footer>
        </div>
    );
};

// Helper Components
const FeatureCard = ({ icon, title, studentBenefit, parentBenefit, bg, border }) => (
    <div className={`bg-gray-800/50 backdrop-blur-sm border ${border} p-8 rounded-3xl hover:-translate-y-2 transition-transform duration-300`}>
        <div className={`${bg} w-14 h-14 rounded-2xl flex items-center justify-center mb-6`}>
            {icon}
        </div>
        <h3 className="text-xl font-black text-white mb-4">{title}</h3>

        <div className="space-y-4">
            <div>
                <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Para o Aluno</p>
                <p className="text-gray-300 leading-snug">{studentBenefit}</p>
            </div>
            <div className="h-px bg-white/5"></div>
            <div>
                <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Para os Pais</p>
                <p className="text-gray-300 leading-snug">{parentBenefit}</p>
            </div>
        </div>
    </div>
);

const TargetIcon = () => (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-pink-400">
        <circle cx="12" cy="12" r="10" />
        <circle cx="12" cy="12" r="6" />
        <circle cx="12" cy="12" r="2" />
    </svg>
);

const TrophyIcon = () => (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-yellow-400">
        <path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6" />
        <path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18" />
        <path d="M4 22h16" />
        <path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22" />
        <path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22" />
        <path d="M18 2H6v7a6 6 0 0 0 12 0V2Z" />
    </svg>
);

export default LandingPage;
