import React from 'react';
import { Upload, RefreshCw } from 'lucide-react';
import LoadingTips from '../UI/LoadingTips';
import DuoButton from '../UI/DuoButton';

const UploadSection = ({ file, handleFileChange, analyzeFile, isAnalyzing }) => {
    return (
        <div className="bg-white rounded-2xl p-8 border-2 border-gray-200 text-center">
            <div className="w-24 h-24 bg-gray-100 rounded-full mx-auto mb-6 flex items-center justify-center text-gray-400">
                <Upload size={40} />
            </div>
            <h2 className="text-2xl font-bold text-gray-700 mb-2">Carrega a Matéria 📚</h2>
            <p className="text-gray-500 mb-8 max-w-sm mx-auto">
                Carrega um PDF ou TXT e a IA cria quizzes personalizados para ti.
            </p>

            <div className="relative inline-block w-full max-w-xs">
                <input
                    type="file"
                    aria-label="Carregar documento de estudo (PDF ou TXT)"
                    accept=".pdf,.txt"
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                />
                <label htmlFor="file-upload">
                    <div className="bg-white border-2 border-duo-blue border-b-4 text-duo-blue font-bold py-3 px-6 rounded-2xl uppercase tracking-wider cursor-pointer hover:bg-blue-50 active:border-b-2 active:translate-y-1 transition-all mb-4 block">
                        {file ? `Selecionado: ${file.name}` : "Escolher Ficheiro"}
                    </div>
                </label>
            </div>

            <DuoButton
                onClick={analyzeFile}
                disabled={!file || isAnalyzing}
                className="max-w-xs mx-auto"
                aria-label={isAnalyzing ? "A analisar ficheiro" : "Começar análise"}
            >
                {isAnalyzing ? <RefreshCw className="animate-spin" /> : "COMEÇAR"}
            </DuoButton>

            {isAnalyzing && <LoadingTips />}
        </div>
    );
};

export default UploadSection;
