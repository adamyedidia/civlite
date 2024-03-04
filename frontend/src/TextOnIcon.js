import React from 'react';
import './TextOnIcon.css';


export const TextOnIcon = ({ image, style, children, tooltip, offset }) => {
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

    const containerStyle = {
        position: 'relative',
        backgroundImage: image ? `url(${image})` : "",
        ...style
    };

    return (
        <div className="icon-bg-text" style={containerStyle}
            onMouseOver={showTooltip} onMouseOut={hideTooltip}>
            <span style={{ textAlign: 'center', marginTop: offset }}>{children}</span>
            {tooltip && (
                <div ref={tooltipRef} className="tooltip">
                    {tooltip}
                </div>
            )}
        </div>
    );
};
