import { useState, useEffect } from 'react';

export const useStudent = () => {
    const [student, setStudent] = useState(() => {
        const saved = localStorage.getItem('study_student');
        return saved ? JSON.parse(saved) : null;
    });

    useEffect(() => {
        if (student) {
            localStorage.setItem('study_student', JSON.stringify(student));
        } else {
            localStorage.removeItem('study_student');
        }
    }, [student]);

    const logout = () => {
        setStudent(null);
    };

    return { student, setStudent, logout };
};
