import api from './api';

export const authService = {
    loginStudent: async (name) => {
        const res = await api.post('/students', { name });
        return res.data;
    }
};
