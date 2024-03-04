import React from 'react';
import './TextOnIcon.css';
import { WithTooltip } from './WithTooltip';


export const TextOnIcon = ({ image, style, children, tooltip, offset }) => {
    const containerStyle = {
        position: 'relative',
        backgroundImage: image ? `url(${image})` : "",
        ...style
    };

    return (
        <WithTooltip tooltip={tooltip}>
        <div className="icon-bg-text" style={containerStyle}>
            <span style={{ textAlign: 'center', marginTop: offset }}>{children}</span>
        </div>
        </WithTooltip>
    );
};
