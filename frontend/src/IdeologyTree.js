import React from "react";
import './IdeologyTree.css';

import { Dialog, DialogTitle, DialogContent, Typography, IconButton } from "@mui/material";
import ideologyImg from "./images/ideology.png";
import { romanNumeral } from "./romanNumeral";

export const TenetDisplay = ({ tenet }) => {
    return <div className="tenet-hover-card">
        <Typography variant="h6" className="tenet-name"> {tenet.name} </Typography>
        <Typography variant="body1" className="tenet-description"> {tenet.description} </Typography>
    </div>
}

const TenetCardSmall = ({ tenet, handleClickTenet, setHoveredTenet, gameState, myGamePlayer }) => {
    const claimedByPlayers = gameState.tenets_claimed_by_player_nums[tenet.name]
    console.log(myGamePlayer.tenets[tenet.name])
    const status = myGamePlayer.tenets[tenet.name] !== undefined ? "taken" : 
        claimedByPlayers.length > 0 ? "unavailable" : 
        myGamePlayer.active_tenet_choice_level == tenet.advancement_level ? "active-choice" : "available";
    return <div className={`tenet-card ${status}`}
        onClick={() => handleClickTenet(tenet)} onMouseEnter={() => setHoveredTenet(tenet)} onMouseLeave={() => setHoveredTenet(null)}>
        <Typography variant="h6" className="tenet-name"> {tenet.name} </Typography>
    </div>
}

const TenetLevelBox = ({ level, tenets, gameState, myGamePlayer, handleClickTenet, setHoveredTenet}) => {
    return <div className="tenet-level-box">
        {romanNumeral(level)}
        {tenets.map((tenet, index) => 
            <TenetCardSmall tenet={tenet} key={index} handleClickTenet={handleClickTenet} setHoveredTenet={setHoveredTenet} gameState={gameState} myGamePlayer={myGamePlayer}/>
        )}
    </div>
}

const IdeologyTreeDialog = ({open, onClose, handleClickTenet, setHoveredTenet, templates, gameState, myGamePlayer }) => {
    if (!templates) return null;
    
    const advancementLevels = Object.values(templates.TENETS).reduce((acc, tenet) => {
        const level = tenet.advancement_level;
        if (!acc[level]) {
            acc[level] = [];
        }
        acc[level].push(tenet);
        return acc;
    }, {});

    const tenetLevelBox = (level) => {
        return <TenetLevelBox level={level} tenets={advancementLevels[level]} gameState={gameState} myGamePlayer={myGamePlayer} handleClickTenet={handleClickTenet} setHoveredTenet={setHoveredTenet}/>
    }

    return (
        <Dialog open={open} onClose={onClose} maxWidth="lg">
            <DialogTitle>
                <Typography variant="h5" component="div" style={{ flexGrow: 1, textAlign: 'center' }}>
                    Ideologies
                </Typography>
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    style={{
                        position: 'absolute',
                        right: 8,
                        top: 8,
                        color: (theme) => theme.palette.grey[500],
                    }}
                    color="primary"
                >
                    Close
                </IconButton>
                <img src={ideologyImg} alt="" style={{
                        height: 'auto', 
                        width: '100px', 
                        position: "absolute",
                        left: "10px",
                        top: "10px",
                        }}/>
            </DialogTitle>
            <DialogContent className="tenet-dialog-content">
                {tenetLevelBox(1)}
                {tenetLevelBox(2)}
            </DialogContent>
        </Dialog>
    )
}


export default IdeologyTreeDialog