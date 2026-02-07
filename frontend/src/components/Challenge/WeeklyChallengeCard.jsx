import { Users, ShieldCheck } from 'lucide-react';
import MissionProgressBar from './MissionProgressBar';

const calcCoopProgress = (status) => {
    const target = Number(status?.team?.mission_base?.target_days_each || 0);
    const studentDays = Number(status?.team?.mission_base?.student_days || 0);
    const partnerDays = Number(status?.team?.mission_base?.partner_days || 0);

    if (target <= 0) return 0;
    const totalTarget = target * 2;
    const done = Math.min(studentDays, target) + Math.min(partnerDays, target);
    return Math.round((done / totalTarget) * 100);
};

const calcContinuityProgress = (status) => {
    const targetXp = Number(status?.continuity_mission?.target_xp || 0);
    const targetDays = Number(status?.continuity_mission?.target_days || 0);
    const xp = Number(status?.individual?.xp || 0);
    const days = Number(status?.individual?.active_days || 0);

    if (targetXp <= 0 || targetDays <= 0) return 0;

    const xpProgress = Math.min(100, Math.round((xp / targetXp) * 100));
    const daysProgress = Math.min(100, Math.round((days / targetDays) * 100));
    return Math.round((xpProgress + daysProgress) / 2);
};

const WeeklyChallengeCard = ({ status, loading, error }) => {
    if (loading) {
        return (
            <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 animate-pulse">
                <h3 className="font-bold text-sm uppercase tracking-wider text-gray-600 mb-3">Desafio das Cientistas</h3>
                <div className="h-5 w-40 bg-gray-100 rounded mb-4" />
                <div className="h-3 w-full bg-gray-100 rounded mb-2" />
                <div className="h-3 w-24 bg-gray-100 rounded" />
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-white rounded-2xl border-2 border-red-200 p-6">
                <h3 className="font-bold text-sm uppercase tracking-wider text-red-600 mb-2">Desafio das Cientistas</h3>
                <p className="text-sm text-red-500">{error}</p>
            </div>
        );
    }

    if (!status) {
        return (
            <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
                <h3 className="font-bold text-sm uppercase tracking-wider text-gray-600 mb-2">Desafio das Cientistas</h3>
                <p className="text-sm text-gray-500">Sem dados esta semana.</p>
            </div>
        );
    }

    const isCoop = status.mode === 'coop';
    const progress = isCoop ? calcCoopProgress(status) : calcContinuityProgress(status);
    const teamXP = Number(status?.team?.team_xp || 0);
    const studentDays = Number(status?.individual?.active_days || 0);
    const partnerDays = Number(status?.partner?.active_days || 0);

    return (
        <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 space-y-4">
            <div className="flex items-start justify-between gap-3">
                <div>
                    <h3 className="font-bold text-gray-700 text-sm uppercase tracking-wider">Desafio das Cientistas</h3>
                    <p className="text-xs text-gray-500 font-bold uppercase tracking-wide">Semana {status.week_id}</p>
                </div>
                <span className={`text-xs font-black uppercase px-2 py-1 rounded-full ${status.status === 'completed' || status.status === 'continuity_completed' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'}`}>
                    {status.status === 'completed' || status.status === 'continuity_completed' ? 'Concluída' : 'Em progresso'}
                </span>
            </div>

            <MissionProgressBar
                value={progress}
                label={isCoop ? 'Missão Base (equipa)' : 'Missão de Continuidade'}
            />

            {isCoop ? (
                <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="bg-blue-50 border border-blue-100 rounded-xl p-3">
                        <p className="text-[11px] uppercase font-bold text-blue-600">XP da Equipa</p>
                        <p className="text-xl font-black text-blue-700">{teamXP}</p>
                    </div>
                    <div className="bg-gray-50 border border-gray-100 rounded-xl p-3">
                        <p className="text-[11px] uppercase font-bold text-gray-500">Dias Ativos</p>
                        <p className="text-lg font-black text-gray-700">{studentDays} / {partnerDays}</p>
                    </div>
                </div>
            ) : (
                <div className="bg-amber-50 border border-amber-100 rounded-xl p-3 text-sm">
                    <div className="flex items-center gap-2 text-amber-700 font-bold uppercase text-[11px]">
                        <ShieldCheck size={14} />
                        Continuidade
                    </div>
                    <p className="text-gray-700 mt-1 font-bold">{Number(status?.individual?.xp || 0)} XP e {studentDays} dias ativos</p>
                </div>
            )}

            <div className="text-xs text-gray-500 flex items-center gap-2 font-bold uppercase tracking-wide">
                <Users size={14} />
                {isCoop
                    ? `Parceira: ${status?.team?.partner_name || '—'}`
                    : 'Modo solo temporário'}
            </div>
        </div>
    );
};

export default WeeklyChallengeCard;
