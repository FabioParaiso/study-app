import { useRef, useLayoutEffect, useState } from 'react';

const TOOLTIP_OFFSET_PX = 8;
const TOOLTIP_EDGE_PADDING = 8;

/**
 * Floating tooltip that positions itself relative to an anchor element.
 * Automatically flips to bottom if there's not enough space at the top.
 */
const FloatingTooltip = ({ anchorRef, text, visible }) => {
    const tooltipRef = useRef(null);
    const [style, setStyle] = useState({ left: 0, top: 0, placement: "top" });

    useLayoutEffect(() => {
        if (!visible) return;

        const updatePosition = () => {
            if (!anchorRef.current || !tooltipRef.current) return;
            const anchorRect = anchorRef.current.getBoundingClientRect();
            const tooltipRect = tooltipRef.current.getBoundingClientRect();

            let top = anchorRect.top - tooltipRect.height - TOOLTIP_OFFSET_PX;
            let placement = "top";
            if (top < TOOLTIP_EDGE_PADDING) {
                top = anchorRect.bottom + TOOLTIP_OFFSET_PX;
                placement = "bottom";
            }

            const centerX = anchorRect.left + anchorRect.width / 2;
            let left = centerX - tooltipRect.width / 2;
            const maxLeft = window.innerWidth - tooltipRect.width - TOOLTIP_EDGE_PADDING;
            left = Math.max(TOOLTIP_EDGE_PADDING, Math.min(left, maxLeft));

            setStyle({ left, top, placement });
        };

        const frameId = requestAnimationFrame(updatePosition);
        window.addEventListener('resize', updatePosition);
        window.addEventListener('scroll', updatePosition, true);

        return () => {
            cancelAnimationFrame(frameId);
            window.removeEventListener('resize', updatePosition);
            window.removeEventListener('scroll', updatePosition, true);
        };
    }, [visible, text, anchorRef]);

    return (
        <div
            ref={tooltipRef}
            role="tooltip"
            aria-hidden={!visible}
            className={`pointer-events-none fixed z-50 rounded-xl bg-white text-gray-700 text-[10px] font-bold px-2.5 py-1.5 border border-gray-200 shadow-md max-w-[220px] whitespace-normal text-center transition-opacity ${visible ? 'opacity-100' : 'opacity-0'}`}
            style={{ left: style.left, top: style.top }}
        >
            {text}
            <span
                className={`absolute left-1/2 -translate-x-1/2 w-0 h-0 border-4 border-transparent ${style.placement === "top" ? "top-full border-t-white" : "bottom-full border-b-white"}`}
            ></span>
        </div>
    );
};

/**
 * Wrapper component that shows a tooltip on hover/focus.
 * Use this to wrap chart bars or other interactive elements.
 */
const TooltipTarget = ({ text, enabled = true, children }) => {
    const anchorRef = useRef(null);
    const [visible, setVisible] = useState(false);

    const show = () => setVisible(true);
    const hide = () => setVisible(false);

    return (
        <div
            ref={anchorRef}
            className="relative flex flex-col items-center"
            onMouseEnter={show}
            onMouseLeave={hide}
            onFocus={show}
            onBlur={hide}
            tabIndex={enabled ? 0 : -1}
            aria-label={text}
        >
            {children}
            {enabled && <FloatingTooltip anchorRef={anchorRef} text={text} visible={visible} />}
        </div>
    );
};

export { FloatingTooltip, TooltipTarget };
export default TooltipTarget;
