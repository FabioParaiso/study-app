const LoadingOverlay = () => (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex flex-col items-center justify-center animate-fade-in">
        <div className="bg-white p-8 rounded-3xl shadow-2xl flex flex-col items-center text-center max-w-sm mx-4">
            <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-6"></div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">A preparar o teu Quiz...</h3>
            <p className="text-gray-500 text-sm">A nossa IA está a ler a matéria e a criar perguntas desafiantes!</p>
        </div>
    </div>
);

export default LoadingOverlay;
