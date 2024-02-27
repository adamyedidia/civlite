import React from 'react';
import './TurnEndedDisplay.css';

export default function TurnEndedDisplay({ gamePlayerByPlayerNum, turnEndedByPlayerNum, animating, isHoveredHex }) {
    return (
        <div className="turn-ended-display">
            {gamePlayerByPlayerNum && Object.keys(gamePlayerByPlayerNum).map((playerNum) => {
                const gamePlayer = gamePlayerByPlayerNum?.[playerNum];
                const turnEnded = turnEndedByPlayerNum?.[playerNum];
                return (
                    <div key={playerNum} className="turn-ended-card">
                        <span>
                            {turnEnded || animating || gamePlayer?.is_bot ? '✅' : '🤔'}
                        </span>
                        <span>
                            {gamePlayer?.username}
                        </span>
                    </div>
                );
            })}
        </div>
    );
};