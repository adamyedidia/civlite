import React from 'react';
import './TurnEndedDisplay.css';

import declineImg from './images/phoenix.png'

export default function TurnEndedDisplay({ gamePlayerByPlayerNum, turnEndedByPlayerNum, animating, isHoveredHex }) {
    return (
        <div className="turn-ended-display">
            {gamePlayerByPlayerNum && Object.keys(gamePlayerByPlayerNum).map((playerNum) => {
                const gamePlayer = gamePlayerByPlayerNum?.[playerNum];
                const turnEnded = turnEndedByPlayerNum?.[playerNum];
                return (
                    <div key={playerNum} className="turn-ended-card">
                        <span>
                            {gamePlayer.civ_id? (turnEnded || animating || gamePlayer?.is_bot ? '✅' : '🤔') :
                            <img src={declineImg} style={{width: '25px', height: '25px'}}/>}
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