import React from 'react';
import "./WithTooltip.css";

export const WithTooltip = ({ tooltip, alignBottom, children }) => {
    const tooltipRef = React.useRef(null);

    const showTooltip = () => {
        if (tooltipRef.current) {
            tooltipRef.current.style.visibility = 'visible';
            tooltipRef.current.style.opacity = '1';
        }
    };

    const hideTooltip = () => {
        if (tooltipRef.current) {
            tooltipRef.current.style.visibility = 'hidden';
            tooltipRef.current.style.opacity = '0';
        }
    };

    return <div className="tooltip-container" onMouseOver={showTooltip} onMouseOut={hideTooltip}>
        {children}
        {tooltip && <div ref={tooltipRef} className={`tooltip ${alignBottom ? 'bottom' : ''}`}>
            {tooltip}
        </div>}
    </div>;
};
