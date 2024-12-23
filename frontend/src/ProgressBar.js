import React, { useState } from 'react';
import './ProgressBar.css';

const ProgressBar = ({barText, darkPercent, lightPercent}) => {
    if (typeof darkPercent !== 'number' || typeof lightPercent !== 'number') {
        throw new Error('darkPercent and lightPercent must be numbers');
    }
    const darkPercentClipped = Math.max(0, Math.min(darkPercent, 100));
    if (darkPercent < 0) {
        lightPercent = lightPercent + darkPercent;
    }
    const lightPercentClipped = Math.max(0, Math.min(lightPercent, 100 - darkPercent));
    return <div className="progress-bar">
                <div className="bar stored" style={{ width: `${darkPercentClipped}%`, }}></div>
                <div className="bar produced" style={{ width: `${lightPercentClipped}%`}}></div>
                <div className="food-progress-text" style={{ position: 'absolute', width: '100%', textAlign: 'center', color: 'black', fontWeight: 'bold' }}>
                    {barText}
                </div>
                {(darkPercent + lightPercent >= 100) && (<div className="checkmark">✅</div>)}
            </div>
}

export default ProgressBar;