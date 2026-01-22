import { useState, useEffect } from 'react';
import { studyService } from '../services/studyService';

const LEVELS = [
    { min: 0, title: "Estudante Curiosa", icon: "Sprout" },
    { min: 100, title: "Exploradora da Natureza", icon: "Compass" },
    { min: 300, title: "Assistente de Laboratório", icon: "Microscope" },
    { min: 600, title: "Bióloga Júnior", icon: "Dna" },
    { min: 1000, title: "Mestre das Ciências", icon: "FlaskConical" },
    { min: 2000, title: "Cientista Lendária", icon: "Rocket" },
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
    const [selectedAvatar, setSelectedAvatar] = useState('mascot');

    // Sync with student and stats
    useEffect(() => {
        if (student) {
            setSelectedAvatar(student.current_avatar || 'mascot');
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
        const previousAvatar = selectedAvatar;

        // Optimistic Update
        setSelectedAvatar(emoji);

        try {
            await studyService.updateAvatar(emoji);
        } catch (e) {
            console.error("Failed to update avatar:", e);
            // Revert on error
            setSelectedAvatar(previousAvatar);
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
