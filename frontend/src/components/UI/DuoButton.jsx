import React from 'react';

const DuoButton = ({ children, onClick, variant = 'primary', disabled, className = '', ...props }) => {
    const variants = {
        primary: 'bg-duo-green border-duo-green-dark text-white hover:bg-[#61E002]',
        secondary: 'bg-duo-blue border-duo-blue-dark text-white hover:bg-[#20BEF5]',
        danger: 'bg-duo-red border-duo-red-dark text-white hover:bg-[#FF5C5C]',
        outline: 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50 border-b-2 active:border-b-2', // Less 3D
        disabled: 'bg-gray-200 border-gray-300 text-gray-400 cursor-not-allowed border-b-0 translate-y-1'
    };

    const style = disabled ? variants.disabled : variants[variant];

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`w-full py-3 px-6 rounded-2xl border-b-4 font-bold uppercase tracking-wider transition-all active:border-b-0 active:translate-y-1 flex items-center justify-center gap-2 ${style} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
};

export default DuoButton;
