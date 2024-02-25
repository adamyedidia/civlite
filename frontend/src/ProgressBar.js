import React, { useState } from 'react';
import './ProgressBar.css';

const ProgressBar = ({barText, darkPercent, lightPercent}) => {
    const darkPercentClipped = Math.min(darkPercent, 100);
    const lightPercentClipped = Math.min(lightPercent, 100 - darkPercent)
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