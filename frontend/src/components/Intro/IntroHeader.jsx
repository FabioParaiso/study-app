import { LogOut, Sprout, Compass, Microscope, Dna, FlaskConical, Rocket, User } from 'lucide-react';
import mascot from '../../assets/mascot.png';

const LevelIcon = ({ iconName, className }) => {
    const icons = {
        Sprout, Compass, Microscope, Dna, FlaskConical, Rocket
    };
    const Icon = icons[iconName] || Sprout;
    return <Icon className={className} />;
};

const IntroHeader = ({ student, selectedAvatar, changeAvatar, totalXP, onLogout, level }) => {
    return (
        <header className="bg-white border-b-2 border-gray-200 sticky top-0 z-10">
            <div className="max-w-5xl mx-auto px-4 h-16 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => changeAvatar(selectedAvatar === 'mascot' ? 'user' : 'mascot')}
                        className="bg-gray-100 hover:bg-gray-200 p-2 rounded-xl border-b-4 border-gray-200 active:border-b-0 active:translate-y-1 transition-all overflow-hidden w-12 h-12 flex items-center justify-center"
                    >
                        {selectedAvatar === 'mascot' ? (
                            <img src={mascot} alt="Mascot" className="w-10 h-10 object-contain" />
                        ) : (
                            <User className="text-gray-400" />
                        )}
                    </button>
                    <div>
                        <h1 className="font-bold text-gray-700 text-lg uppercase tracking-wide">
                            {student.name}
                        </h1>
                        <div className="flex items-center gap-2 text-xs font-bold text-gray-400 uppercase">
                            <LevelIcon iconName={level.icon} className="w-4 h-4 text-duo-green" />
                            <span>{level.title}</span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        <img src="https://d35aaqx5ub95lt.cloudfront.net/images/icons/398e4298a3b39ce566050e5c041949ef.svg" className="w-6 h-6" alt="gem" />
                        <span className="font-bold text-duo-red text-lg">{totalXP} XP</span>
                    </div>
                    <button
                        onClick={onLogout}
                        className="flex items-center gap-2 text-xs font-bold text-duo-gray-dark hover:text-duo-red uppercase tracking-wider px-3 py-1 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                        <span>Bazar</span>
                        <LogOut size={16} />
                    </button>
                </div>
            </div>
        </header>
    );
};

export default IntroHeader;
