import React from "react";
import './IdeologyTree.css';

import { Dialog, DialogTitle, DialogContent, Typography, IconButton, Tooltip } from "@mui/material";
import ideologyImg from "./images/ideology.png";
import { romanNumeral } from "./romanNumeral";
import { IDEOLOGY_LEVEL_STRINGS } from "./ideologyLevelStrings";
import { TextOnIcon } from "./TextOnIcon";
import vpImg from "./images/crown.png";

export const TenetDisplay = ({ tenet }) => {
    return <div className="tenet-hover-card">
        <Typography variant="h6" className="tenet-name"> {tenet.name} </Typography>
        {tenet.quest_description &&
            <Typography variant="body1" className="tenet-quest-description"> Quest: {tenet.quest_description} </Typography>
        }
        <Typography variant="body1" className="tenet-description" style={{opacity: tenet.quest_description ? 0.5 : 1}}> {tenet.description} </Typography>
    </div>
}

const TenetCardSmall = ({ tenet, handleClickTenet, setHoveredTenet, gameState, myGamePlayer }) => {
    const claimedByPlayers = gameState.tenets_claimed_by_player_nums[tenet.name]
    const duplicateClaimable = gameState.duplicate_tenets_claimable[tenet.advancement_level] && claimedByPlayers.length === 1
    const status = (
        claimedByPlayers.length >= 2 ? "unavailable" :
        (claimedByPlayers.length === 1 && !duplicateClaimable) ? "unavailable" :
        myGamePlayer.active_tenet_choice_level === tenet.advancement_level ? "active-choice" : 
        "available"
    );
    const extraA6Info = myGamePlayer.a6_tenet_info?.[tenet.name];
    const title = extraA6Info ? extraA6Info.full_name : tenet.name;
    return <div className={`tenet-card ${status}`}
        onClick={status === "active-choice" ? () => handleClickTenet(tenet) : null} onMouseEnter={() => setHoveredTenet(tenet)} onMouseLeave={() => setHoveredTenet(null)}>
        {duplicateClaimable && <Tooltip title="This tenet has already been claimed. You can still claim it because of the player count, but claiming it will cost 5 VP.">
            <div className="tenet-card-duplicate-claimable-indicator">
                <TextOnIcon image={vpImg} style={{height: "30px", width: "30px"}} offset={10}>-5</TextOnIcon>
            </div>
        </Tooltip>}
        <Typography variant="h6" className="tenet-name"> {title} </Typography>
        {extraA6Info && <Typography variant="body1" style={{textAlign: "center"}}> {extraA6Info.score} vps</Typography>}
    </div>
}

const TenetLevelBox = ({ level, tenets, gameState, myGamePlayer, handleClickTenet, setHoveredTenet}) => {
    const myTenet = tenets.find(tenet => myGamePlayer.tenets[tenet.name] !== undefined);
    const future = myTenet === undefined && level > myGamePlayer.active_tenet_choice_level;
    const status = future ? "future" : level === myGamePlayer.active_tenet_choice_level ? "active-choice" : "";
    const sortedTenets = tenets.sort((a, b) => a.sort_order.localeCompare(b.sort_order));
    return <div className={`tenet-level-box ${status}`}>
        <div className="tenet-level-box-header">
            {romanNumeral(level)}. {IDEOLOGY_LEVEL_STRINGS[level].header}
        </div>
        <div className="tenet-level-box-content">
        {myTenet !== undefined ? 
            <ChosenTenetLevelBox tenet={myTenet} setHoveredTenet={setHoveredTenet} myGamePlayer={myGamePlayer}/> 
            :
            <>
            <Typography variant="h5" className='ideology-question'>
                {IDEOLOGY_LEVEL_STRINGS[level].question}
            </Typography>
            <div className="tenet-choices-list">
                {sortedTenets.map((tenet, index) => 
                    <TenetCardSmall tenet={tenet} key={index} handleClickTenet={handleClickTenet} setHoveredTenet={setHoveredTenet} gameState={gameState} myGamePlayer={myGamePlayer}/>
                )}
            </div>
            </>
        }
        </div>
    </div>
}

const ChosenTenetLevelBox = ({ tenet, setHoveredTenet, myGamePlayer }) => {
    const questIncomplete = tenet.advancement_level === 3 && !myGamePlayer.tenet_quest.complete
    const name = tenet.advancement_level === 6 ? myGamePlayer.a6_tenet_info[tenet.name].full_name : tenet.name;
    return <div className="chosen-tenet-level-box" onMouseEnter={() => setHoveredTenet(tenet)} onMouseLeave={() => setHoveredTenet(null)}>
        <Typography variant="h6" className="tenet-name"> {name} </Typography>
        <Typography variant="body1" className="tenet-description"> 
            {questIncomplete ? 
                `Quest [${myGamePlayer.tenet_quest.progress}/${myGamePlayer.tenet_quest.target}]: ${tenet.quest_description}`
                : tenet.description
            } 
        </Typography>
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
                {Object.keys(advancementLevels).map(level => tenetLevelBox(parseInt(level)))}
            </DialogContent>
        </Dialog>
    )
}


export default IdeologyTreeDialog