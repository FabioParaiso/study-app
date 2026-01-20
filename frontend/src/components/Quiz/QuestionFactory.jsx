import React from 'react';
import QuestionCard from '../QuestionCard';
import OpenEndedCard from '../OpenEndedCard';

export const QuestionFactory = ({
    type,
    question,
    index,
    total,
    userAnswer,
    evaluation,
    isEvaluating,
    onAnswer,
    onEvaluate,
    onNext,
    handleSpeak,
    speakingPart,
    showFeedback
}) => {
    switch (type) {
        case 'multiple':
            return (
                <QuestionCard
                    key={index}
                    question={question}
                    index={index}
                    total={total}
                    onAnswer={onAnswer}
                    userAnswer={userAnswer}
                    onNext={onNext}
                    handleSpeak={handleSpeak}
                    speakingPart={speakingPart}
                    showFeedback={showFeedback}
                />
            );
        case 'open_ended':
            return (
                <OpenEndedCard
                    key={index}
                    question={question}
                    index={index}
                    total={total}
                    onEvaluate={onEvaluate}
                    evaluation={evaluation}
                    isEvaluating={isEvaluating}
                    onNext={onNext}
                    handleSpeak={handleSpeak}
                    speakingPart={speakingPart}
                />
            );
        default:
            return <div className="p-4 text-red-500">Unknown Question Type: {type}</div>;
    }
};
