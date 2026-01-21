import { useState, useEffect, useCallback } from 'react';

export const useSpeechRecognition = () => {
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const [recognition, setRecognition] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recog = new SpeechRecognition();
            recog.continuous = false; // Stop after one sentence/pause
            recog.interimResults = true; // Show results as they speak
            recog.lang = 'pt-PT';

            recog.onstart = () => setIsListening(true);
            recog.onend = () => setIsListening(false);
            recog.onerror = (event) => {
                console.error("Speech recognition error", event.error);
                setError(event.error);
                setIsListening(false);
            };
            recog.onresult = (event) => {
                let current = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    current += event.results[i][0].transcript;
                }
                setTranscript(current);
            };

            setRecognition(recog);
        } else {
            setError("Browser not supported");
        }
    }, []);

    const startListening = useCallback(() => {
        if (recognition) {
            setTranscript('');
            setError(null);
            try {
                recognition.start();
            } catch (e) {
                console.error(e);
            }
        }
    }, [recognition]);

    const stopListening = useCallback(() => {
        if (recognition) {
            recognition.stop();
        }
    }, [recognition]);

    return {
        isListening,
        transcript,
        startListening,
        stopListening,
        error,
        supported: !!recognition
    };
};
