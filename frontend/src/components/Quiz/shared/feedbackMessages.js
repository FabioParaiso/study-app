/**
 * Mensagens motivacionais centralizadas para feedback de Quiz.
 * Evita duplicação de arrays em múltiplos componentes.
 */

export const SUCCESS_MESSAGES = [
    { text: "Fantástico!", icon: "PartyPopper" },
    { text: "Muito bem!", icon: "Star" },
    { text: "Acertaste!", icon: "CheckCircle" },
    { text: "Excelente!", icon: "Trophy" },
    { text: "Boa resposta!", icon: "Flame" }
];

export const ERROR_MESSAGES = [
    { text: "Fica a saber que:", icon: "Brain" },
    { text: "Ups! Vamos ver...", icon: "Search" },
    { text: "Quase! Olha só:", icon: "Lightbulb" }
];

export const PARTIAL_SUCCESS_MESSAGES = [
    { text: "Quase! Olha só:", icon: "Eye" },
    { text: "Não desanimes!", icon: "BicepsFlexed" },
    { text: "Fica a saber que:", icon: "Brain" }
];

/**
 * Retorna uma mensagem aleatória do array fornecido.
 */
/**
 * Retorna um objeto de mensagem aleatória.
 */
export const getRandomMessage = (messages) => {
    return messages[Math.floor(Math.random() * messages.length)];
};
