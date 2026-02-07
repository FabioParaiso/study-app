const clampPercent = (value) => Math.max(0, Math.min(100, Number(value) || 0));

const MissionProgressBar = ({ value = 0, label = '' }) => {
    const safe = clampPercent(value);

    return (
        <div className="space-y-2">
            {label ? <p className="text-xs font-bold uppercase tracking-wider text-gray-500">{label}</p> : null}
            <div className="w-full bg-gray-100 rounded-full h-3 border border-gray-200 overflow-hidden">
                <div
                    className="h-full bg-duo-green transition-all duration-500"
                    style={{ width: `${safe}%` }}
                    role="progressbar"
                    aria-valuemin={0}
                    aria-valuemax={100}
                    aria-valuenow={safe}
                    aria-label={label || 'Progresso da missão'}
                />
            </div>
            <p className="text-xs font-bold text-gray-500">{safe}%</p>
        </div>
    );
};

export default MissionProgressBar;
