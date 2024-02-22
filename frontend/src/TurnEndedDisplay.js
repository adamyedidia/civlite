import React from 'react';
import './TurnEndedDisplay.css';

export default function TurnEndedDisplay({ gamePlayerByPlayerNum, turnEndedByPlayerNum, animating, isHoveredHex }) {
    return (
        <div className="turn-ended-display" style={isHoveredHex ? {left: '200px'} : {}}>
            {gamePlayerByPlayerNum && Object.keys(gamePlayerByPlayerNum).map((playerNum) => {
                const gamePlayer = gamePlayerByPlayerNum?.[playerNum];
                const turnEnded = turnEndedByPlayerNum?.[playerNum];
                return (
                    <div key={playerNum} className="turn-ended-card">
                        <p style={{fontSize: '20px'}}>{`${gamePlayer?.username} ${turnEnded || animating || gamePlayer?.is_bot ? '✅' : '🤔'}`}</p>
                    </div>
                );
            })}
        </div>
    );
};