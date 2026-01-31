import api from './api';

export const authService = {
    loginStudent: async (name, password) => {
        const res = await api.post('/login', { name, password });
        if (res.data.access_token) {
            localStorage.setItem('study_token', res.data.access_token);
        }
        return res.data.user;
    },
    registerStudent: async (name, password, inviteCode) => {
        const res = await api.post('/register', { name, password, invite_code: inviteCode });
        if (res.data.access_token) {
            localStorage.setItem('study_token', res.data.access_token);
        }
        return res.data.user;
    },
    logout: () => {
        localStorage.removeItem('study_token');
    }
};
