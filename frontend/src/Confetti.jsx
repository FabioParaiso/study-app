import React, { useEffect, useRef } from 'react';

const Confetti = () => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const particles = [];
        const colors = ['#f00', '#0f0', '#00f', '#ff0', '#0ff', '#f0f'];

        for (let i = 0; i < 200; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height - canvas.height,
                color: colors[Math.floor(Math.random() * colors.length)],
                size: Math.random() * 5 + 2,
                speed: Math.random() * 3 + 2,
                angle: Math.random() * 6.2
            });
        }

        let animationId;
        const animate = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach(p => {
                p.y += p.speed;
                p.x += Math.sin(p.angle);
                p.angle += 0.1;
                if (p.y > canvas.height) p.y = -10;
                ctx.fillStyle = p.color;
                ctx.fillRect(p.x, p.y, p.size, p.size);
            });
            animationId = requestAnimationFrame(animate);
        };

        animate();

        // Auto-stop after 5 seconds to save performance
        const timer = setTimeout(() => cancelAnimationFrame(animationId), 5000);

        return () => {
            cancelAnimationFrame(animationId);
            clearTimeout(timer);
        }
    }, []);

    return <canvas ref={canvasRef} className="fixed top-0 left-0 w-full h-full pointer-events-none z-50" />;
};

export default Confetti;
