import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import App from './App';

let mockStudent = null;
let mockGameState = 'intro';

const mockSetStudent = vi.fn((nextStudent) => {
    mockStudent = nextStudent;
});

const mockLogout = vi.fn(() => {
    mockStudent = null;
});

const mockSetGameState = vi.fn((nextState) => {
    mockGameState = typeof nextState === 'function' ? nextState(mockGameState) : nextState;
});

vi.mock('./hooks/useStudent', () => ({
    useStudent: () => ({
        student: mockStudent,
        setStudent: mockSetStudent,
        logout: mockLogout,
    }),
}));

vi.mock('./hooks/useMaterial', () => ({
    useMaterial: () => ({
        file: null,
        savedMaterial: null,
        availableTopics: [],
        selectedTopic: 'all',
        isAnalyzing: false,
        errorMsg: '',
        setSelectedTopic: vi.fn(),
        handleFileChange: vi.fn(),
        analyzeFile: vi.fn(),
        detectTopics: vi.fn(),
        clearMaterial: vi.fn(),
        materialsList: [],
        activateMaterial: vi.fn(),
        refreshMaterial: vi.fn(),
        deleteMaterial: vi.fn(),
    }),
}));

vi.mock('./hooks/useGamification', () => ({
    useGamification: () => ({
        highScore: 0,
        totalXP: 0,
        selectedAvatar: 'avatar_1',
        changeAvatar: vi.fn(),
        addXP: vi.fn(),
        updateHighScore: vi.fn(),
        level: { title: 'Iniciante', min: 0 },
        nextLevel: null,
        LEVELS: [{ title: 'Iniciante', min: 0 }],
    }),
}));

vi.mock('./hooks/useQuiz', () => ({
    useQuiz: () => ({
        questions: [],
        loading: false,
        errorMsg: '',
        quizType: 'multiple-choice',
        gameState: mockGameState,
        setGameState: mockSetGameState,
        currentQuestionIndex: 0,
        score: 0,
        streak: 0,
        userAnswers: [],
        openEndedEvaluations: [],
        isEvaluating: false,
        startQuiz: vi.fn(),
        handleAnswer: vi.fn(),
        handleEvaluation: vi.fn(),
        handleShortAnswer: vi.fn(),
        nextQuestion: vi.fn(),
        exitQuiz: vi.fn(),
        getOpenEndedAverage: vi.fn(() => 0),
        showFeedback: false,
        missedIndices: [],
        startReviewMode: vi.fn(),
        sessionXP: 0,
    }),
}));

vi.mock('./hooks/useTTS', () => ({
    useTTS: () => ({
        speakingPart: null,
        handleSpeak: vi.fn(),
    }),
}));

vi.mock('./pages/LoginPage', () => ({
    default: () => <div data-testid="login-page">LoginPage</div>,
}));

vi.mock('./pages/IntroPage', () => ({
    default: ({ onLogout }) => (
        <div data-testid="intro-page">
            IntroPage
            <button type="button" onClick={onLogout}>logout</button>
        </div>
    ),
}));

vi.mock('./pages/AnalyticsPage', () => ({
    default: () => <div data-testid="analytics-page">AnalyticsPage</div>,
}));

vi.mock('./pages/QuizPage', () => ({
    default: () => <div data-testid="quiz-page">QuizPage</div>,
}));

vi.mock('./pages/ResultsPage', () => ({
    default: () => <div data-testid="results-page">ResultsPage</div>,
}));

vi.mock('./components/LoadingOverlay', () => ({
    default: () => <div data-testid="loading-overlay">LoadingOverlay</div>,
}));

describe('App', () => {
    beforeEach(() => {
        mockStudent = null;
        mockGameState = 'intro';
        vi.clearAllMocks();
    });

    it('renders LoginPage when user is not authenticated', () => {
        render(<App />);

        expect(screen.getByTestId('login-page')).toBeInTheDocument();
        expect(screen.queryByTestId('intro-page')).not.toBeInTheDocument();
    });

    it('renders IntroPage when user is authenticated and gameState is intro', () => {
        mockStudent = { id: 1, name: 'Alice' };
        mockGameState = 'intro';

        render(<App />);

        expect(screen.getByTestId('intro-page')).toBeInTheDocument();
        expect(screen.queryByTestId('login-page')).not.toBeInTheDocument();
    });

    it('returns to LoginPage after logout from IntroPage', () => {
        mockStudent = { id: 1, name: 'Alice' };
        mockGameState = 'intro';

        const { rerender } = render(<App />);

        fireEvent.click(screen.getByRole('button', { name: 'logout' }));
        rerender(<App />);

        expect(mockLogout).toHaveBeenCalledTimes(1);
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
        expect(screen.queryByTestId('intro-page')).not.toBeInTheDocument();
    });
});
