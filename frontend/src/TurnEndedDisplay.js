import React from 'react';
import './TurnEndedDisplay.css';

export default function TurnEndedDisplay({ gamePlayerByPlayerNum, turnEndedByPlayerNum, animating }) {

    return (
        <div className="turn-ended-display">
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