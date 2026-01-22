import React, { useEffect, useState } from 'react';
import { Flame, Zap, Rocket } from 'lucide-react';

const ComboCounter = ({ combo }) => {
    const [scale, setScale] = useState(1);

    useEffect(() => {
        if (combo > 1) {
            setScale(1.5);
            const timer = setTimeout(() => setScale(1), 200);
            return () => clearTimeout(timer);
        }
    }, [combo]);

    if (combo < 2) return null;

    let color = "text-orange-500";
    let Icon = Flame;

    if (combo >= 5) { color = "text-purple-500"; Icon = Zap; }
    if (combo >= 10) { color = "text-red-600"; Icon = Rocket; }

    return (
        <div
            className={`fixed top-24 right-4 z-50 transform transition-transform duration-200 flex flex-col items-center bg-white border-b-4 border-gray-200 p-2 rounded-xl shadow-lg`}
            style={{ transform: `scale(${scale}) rotate(-5deg)` }}
        >
            <div className={`text-2xl font-black ${color}`}>
                {combo}x
            </div>
            <div className={`text-xs font-bold uppercase text-gray-400 flex items-center justify-center gap-1`}>
                Combo <Icon size={16} className={color} fill="currentColor" />
            </div>
        </div>
    );
};

export default ComboCounter;
