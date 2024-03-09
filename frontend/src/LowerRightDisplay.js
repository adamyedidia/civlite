import React from 'react';

import './LowerRightDisplay.css';

import AnnouncementsDisplay from './AnnouncementsDisplay';
import Timer from './Timer';
import TurnEndedDisplay from './TurnEndedDisplay';
import EngineStates from './EngineStates';

import { Button, CircularProgress } from '@mui/material';

const AnimationControlBar = ({animationFrame, animationTotalFrames}) => {
    return <div className="animation-control-bar">
        <div className="animation-progress-bar">
            <div className="animation-bar-dot" style={{left: `${animationFrame / animationTotalFrames * 100}%`}}>
            </div>
        </div>
        <div className="animation-control-bar-stop" >
        </div>
    </div>
}

const LowerRightDisplay = ({ gameState, gameId, playerNum, timerMuted, turnEndedByPlayerNum, hoveredHex, handleClickEndTurn, handleClickUnendTurn, triggerAnimations, engineState, animationFrame, animationTotalFrames, cancelAnimations }) => {
    const toggleAnimations = () => {
        if (engineState === EngineStates.ANIMATING) {
            cancelAnimations();
        } else if (engineState === EngineStates.PLAYING) {
            triggerAnimations(gameState);
        }
    }
    
    return <div className="lower-right-display">
        <AnnouncementsDisplay announcements={gameState?.announcements} />
        <div className="end-turn-area">
            <div className="turn-roll-buttons">
                {gameState?.special_mode_by_player_num?.[playerNum] !== 'starting_location' && <Button
                    style={{backgroundColor: "#cccc88", fontSize:"2em", height: "120px", padding: "5px"}} 
                    variant="contained"
                    onClick={turnEndedByPlayerNum?.[playerNum] ? handleClickUnendTurn : handleClickEndTurn}
                    disabled={engineState !== EngineStates.PLAYING}
                >
                    {engineState === EngineStates.PLAYING && 
                        (turnEndedByPlayerNum?.[playerNum] ? "Unend turn" : gameState?.special_mode_by_player_num?.[playerNum] === "choose_decline_option" ? "End turn (mulligan)" : "End turn")
                    }
                    {engineState === EngineStates.GAME_OVER && "Game Over" }
                    {engineState === EngineStates.ROLLING && <>
                        <CircularProgress size={24} />
                        <p style={{fontSize: "0.5em"}}>Waiting for server</p>
                    </>}
                    {engineState === EngineStates.ANIMATING && <>
                        <CircularProgress size={24} />
                        <p style={{fontSize: "0.5em"}}>Animating...</p>
                    </>}
                </Button>}
                {!gameState?.special_mode_by_player_num?.[playerNum] && <Button
                    style={{backgroundColor: "#ffcccc",}} 
                    variant="contained"
                    onClick={toggleAnimations}
                    disabled={engineState !== EngineStates.PLAYING && engineState !== EngineStates.ANIMATING}
                >
                    {engineState === EngineStates.ANIMATING ? 
                        <AnimationControlBar 
                            animationFrame={animationFrame}
                            animationTotalFrames={animationTotalFrames}
                        />

                    : "Replay animations" }
                </Button>}
            </div>
            <TurnEndedDisplay 
                gamePlayerByPlayerNum={gameState?.game_player_by_player_num}
                turnEndedByPlayerNum={turnEndedByPlayerNum}
            />
            {gameState?.next_forced_roll_at && <Timer nextForcedRollAt={gameState?.next_forced_roll_at} gameId={gameId} disabledText={timerMuted && "Paused"}/>}
            
        </div>
    </div>
}

export default LowerRightDisplay;
