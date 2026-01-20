import { useState, useEffect } from 'react';

const LEVELS = [
    { min: 0, title: "Estudante Curiosa", emoji: "🌱" },
    { min: 100, title: "Exploradora da Natureza", emoji: "🦋" },
    { min: 300, title: "Assistente de Laboratório", emoji: "🔬" },
    { min: 600, title: "Bióloga Júnior", emoji: "🧬" },
    { min: 1000, title: "Mestre das Ciências", emoji: "👩‍🔬" },
    { min: 2000, title: "Cientista Lendária", emoji: "🚀" },
];

const getLevelInfo = (xp) => {
    let level = LEVELS[0];
    let nextLevel = LEVELS[1];
    for (let i = 0; i < LEVELS.length; i++) {
        if (xp >= LEVELS[i].min) {
            level = LEVELS[i];
            nextLevel = LEVELS[i + 1] || null;
        }
    }
    return { level, nextLevel };
};

export function useGamification(student, stats) {
    const [highScore, setHighScore] = useState(0);
    const [totalXP, setTotalXP] = useState(0);
    const [selectedAvatar, setSelectedAvatar] = useState('👩‍🎓');

    // Sync with student and stats
    useEffect(() => {
        if (student) {
            setSelectedAvatar(student.current_avatar || '👩‍🎓');
        }
        if (stats) {
            setHighScore(stats.high_score || 0);
            setTotalXP(stats.total_xp || 0);
        } else {
            setHighScore(0);
            setTotalXP(0);
        }
    }, [student, stats]);



    const changeAvatar = async (emoji) => {
        if (!student?.id) return;
        try {
            setSelectedAvatar(emoji);
            await studyService.updateAvatar(student.id, emoji);
        } catch (e) {
            console.error("Failed to update avatar:", e);
        }
    };

    const addXP = (amount) => {
        // Optimistic / Local only. Backend is updated via Quiz Submission.
        setTotalXP(prev => prev + amount);
    };

    const updateHighScore = (score) => {
        if (score > highScore) {
            setHighScore(score);
        }
    };

    const { level, nextLevel } = getLevelInfo(totalXP);

    return {
        highScore,
        totalXP,
        selectedAvatar,
        changeAvatar,
        addXP,
        updateHighScore,
        level,
        nextLevel,
        LEVELS
    };
}
