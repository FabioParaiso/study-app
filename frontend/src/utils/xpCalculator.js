/**
 * Utilitário para cálculo de XP baseado em pontuação.
 * Centraliza lógica duplicada em useQuiz.js.
 */

/**
 * Calcula XP ganho com base na pontuação de avaliação.
 * - Base: 5 XP
 * - Bónus >= 50: +5 XP
 * - Bónus >= 80: +5 XP adicional
 * 
 * @param {number} score - Pontuação de 0 a 100
 * @returns {number} XP ganho
 */
export const calculateXPFromScore = (score) => {
    let xp = 5; // Base XP for attempting
    if (score >= 50) xp += 5;
    if (score >= 80) xp += 5;
    return xp;
};
