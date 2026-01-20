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

export function useGamification() {
    const [highScore, setHighScore] = useState(0);
    const [totalXP, setTotalXP] = useState(0);
    const [selectedAvatar, setSelectedAvatar] = useState('👩‍🎓');

    useEffect(() => {
        const savedScore = localStorage.getItem('scienceQuizHighScore');
        if (savedScore) setHighScore(parseInt(savedScore, 10));

        const savedXP = localStorage.getItem('scienceQuizTotalXP');
        if (savedXP) setTotalXP(parseInt(savedXP, 10));

        const savedAvatar = localStorage.getItem('scienceQuizAvatar');
        if (savedAvatar) setSelectedAvatar(savedAvatar);
    }, []);

    const changeAvatar = (emoji) => {
        setSelectedAvatar(emoji);
        localStorage.setItem('scienceQuizAvatar', emoji);
    };

    const addXP = (amount) => {
        const newXP = totalXP + amount;
        setTotalXP(newXP);
        localStorage.setItem('scienceQuizTotalXP', newXP.toString());
    };

    const updateHighScore = (score) => {
        if (score > highScore) {
            setHighScore(score);
            localStorage.setItem('scienceQuizHighScore', score.toString());
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
