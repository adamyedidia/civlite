import React from 'react';
import './TurnEndedDisplay.css';

import declineImg from './images/phoenix.png'

export default function TurnEndedDisplay({ gamePlayerByPlayerNum, turnEndedByPlayerNum, isOvertime }) {
    return (
        <div className="turn-ended-display">
            {gamePlayerByPlayerNum && Object.keys(gamePlayerByPlayerNum).map((playerNum) => {
                const gamePlayer = gamePlayerByPlayerNum?.[playerNum];
                const turnEnded = turnEndedByPlayerNum?.[playerNum];
                return (
                    <div key={playerNum} className="turn-ended-card">
                        <span>
                            {turnEnded || gamePlayer?.is_bot ? '✅' : 
                            isOvertime ?  <img src={declineImg} width={20} height={20}/>: '🤔'}
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