import { useState, useCallback } from 'react';

const cleanTextForSpeech = (text) => {
    if (!text) return "";
    return text
        .replace(/->/g, "dá origem a")
        .replace(/\*/g, "")
        .replace(/_/g, "");
};

export const useTTS = () => {
    const [speakingPart, setSpeakingPart] = useState(null);

    // Cancel speech when component unmounts or specific states change (handled by effect in consumer usually, but we can expose a cancel)
    const cancelSpeech = useCallback(() => {
        window.speechSynthesis.cancel();
        setSpeakingPart(null);
    }, []);

    const handleSpeak = useCallback((text, part) => {
        if (speakingPart === part) {
            cancelSpeech();
            return;
        }

        // Cancel any current speech
        window.speechSynthesis.cancel();

        const cleanText = cleanTextForSpeech(text);
        if (!cleanText) return;

        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'pt-PT';

        setSpeakingPart(part);

        utterance.onend = () => setSpeakingPart(null);
        utterance.onerror = () => setSpeakingPart(null);

        window.speechSynthesis.speak(utterance);
    }, [speakingPart, cancelSpeech]);

    return { speakingPart, handleSpeak, cancelSpeech };
};
