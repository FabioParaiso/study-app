import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import WeeklyChallengeCard from './WeeklyChallengeCard';

describe('WeeklyChallengeCard', () => {
    it('renders loading state', () => {
        render(<WeeklyChallengeCard loading status={null} error="" />);
        expect(screen.getByText(/Desafio das Cientistas/i)).toBeInTheDocument();
    });

    it('renders error state', () => {
        render(<WeeklyChallengeCard loading={false} status={null} error="Falha" />);
        expect(screen.getByText('Falha')).toBeInTheDocument();
    });

    it('renders coop mode payload', () => {
        const status = {
            week_id: '2026W07',
            mode: 'coop',
            status: 'in_progress',
            team: {
                partner_name: 'Maria',
                team_xp: 100,
                mission_base: {
                    target_days_each: 3,
                    student_days: 3,
                    partner_days: 2
                }
            },
            individual: { active_days: 3 },
            partner: { active_days: 2 }
        };

        render(<WeeklyChallengeCard loading={false} status={status} error="" />);

        expect(screen.getByText(/XP da Equipa/i)).toBeInTheDocument();
        expect(screen.getByText(/Parceira: Maria/i)).toBeInTheDocument();
    });

    it('renders solo continuity mode payload', () => {
        const status = {
            week_id: '2026W07',
            mode: 'solo_continuity',
            status: 'continuity_in_progress',
            continuity_mission: {
                target_xp: 75,
                target_days: 3
            },
            individual: {
                xp: 40,
                active_days: 2
            }
        };

        render(<WeeklyChallengeCard loading={false} status={status} error="" />);

        expect(screen.getByText(/Missão de Continuidade/i)).toBeInTheDocument();
        expect(screen.getByText(/Modo solo temporário/i)).toBeInTheDocument();
    });
});
