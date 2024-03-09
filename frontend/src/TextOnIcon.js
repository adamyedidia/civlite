import React from 'react';
import './TextOnIcon.css';
import { WithTooltip } from './WithTooltip';


export const TextOnIcon = ({ image, style, children, tooltip, offset }) => {
    const containerStyle = {
        position: 'relative',
        backgroundImage: image ? `url(${image})` : "",
        ...style
    };

    let content = <div className="icon-bg-text" style={containerStyle}>
        <span style={{ textAlign: 'center', marginTop: offset }}>{children}</span>
    </div>;

    if (tooltip) {
        content = <WithTooltip tooltip={tooltip}>
            {content}
        </WithTooltip>;
    }

    return content;
};
