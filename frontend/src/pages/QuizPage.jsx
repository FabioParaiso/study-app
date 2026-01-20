import React from 'react';
import { X } from 'lucide-react';
import { QuestionFactory } from '../components/Quiz/QuestionFactory';

const QuizPage = ({
    questions,
    currentQuestionIndex,
    quizType,
    userAnswers,
    openEndedEvaluations,
    isEvaluating,
    onAnswer,
    onEvaluate,
    onNext,
    onExit,
    handleSpeak,
    speakingPart,
    showFeedback,
    addXP // Passed down if needed by handlers
}) => {
    const currentQ = questions[currentQuestionIndex];

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6 relative">
            {/* Header */}
            <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-center z-50">
                <button
                    onClick={() => {
                        if (window.confirm("Tens a certeza que queres sair? Vais perder o progresso atual.")) {
                            onExit();
                        }
                    }}
                    className="p-3 rounded-2xl bg-white border-b-4 border-gray-200 text-gray-400 hover:bg-gray-50 hover:text-red-500 hover:border-red-200 transition-all active:border-b-0 active:translate-y-1"
                    aria-label="Sair"
                >
                    <X size={24} strokeWidth={3} />
                </button>
            </div>

            <QuestionFactory
                type={quizType}
                question={currentQ}
                index={currentQuestionIndex}
                total={questions.length}
                userAnswer={userAnswers[currentQuestionIndex] !== undefined ? userAnswers[currentQuestionIndex] : null}
                evaluation={openEndedEvaluations[currentQuestionIndex]}
                isEvaluating={isEvaluating}
                onAnswer={(qId, oId) => onAnswer(qId, oId, addXP)}
                onEvaluate={(text) => onEvaluate(text, addXP)}
                onNext={onNext}
                handleSpeak={handleSpeak}
                speakingPart={speakingPart}
                showFeedback={showFeedback}
            />
        </div>
    );
};

export default QuizPage;
