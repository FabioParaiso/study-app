/**
 * Mensagens motivacionais centralizadas para feedback de Quiz.
 * Evita duplicação de arrays em múltiplos componentes.
 */

export const SUCCESS_MESSAGES = [
    "Fantástico! 🎉",
    "Muito bem! 🌟",
    "Acertaste! 💪"
];

export const ERROR_MESSAGES = [
    "Fica a saber que: 🧠",
    "Ups! Vamos ver... 🤔",
    "Quase! Olha só: 💡"
];

export const PARTIAL_SUCCESS_MESSAGES = [
    "Quase! Olha só: 👀",
    "Não desanimes! 💪",
    "Fica a saber que: 🧠"
];

/**
 * Retorna uma mensagem aleatória do array fornecido.
 */
export const getRandomMessage = (messages) => {
    return messages[Math.floor(Math.random() * messages.length)];
};
