import React from "react";
import './TechListDialog.css';

import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography, IconButton } from "@mui/material";
import { IconUnitDisplay } from "./UnitDisplay";
import { BriefBuildingDisplay } from "./BuildingDisplay";
import scienceImg from './images/science.png';

const TechColumn = ({children}) => {
    return <div className="tech-column">{children}</div>
}

export const romanNumeral = (level) => { return level === 1 ? 'I' : level === 2 ? 'II' : level === 3 ? 'III' : level === 4 ? 'IV' : level === 5 ? 'V' : level === 6 ? 'VI' : level === 7 ? 'VII' : level === 8 ? 'VIII' : level === 9 ? 'IX' : level === 10 ? 'X' : level === 11 ? 'XI' : level === 12 ? 'XII' : level === 13 ? 'XIII' : '???';}

const TechLevelBox = ({level, techs, myCiv, gameState, techTemplates, unitTemplates, buildingTemplates, setHoveredTech, handleClickTech}) => {
    const levelRomanNumeral = romanNumeral(level);

    // Need to keep this in sync with python code. Might be better to pass it down.
    const myTechs = myCiv.num_researched_techs;
    const unlockedLevel = 1 + Math.floor(myTechs / 3);
    const techsToUnlockNextLevel = 3 * unlockedLevel;
    return (
        <div className={`tech-level-box ${unlockedLevel < level ? 'disabled' : ''}`}>
            <div className='tech-level-box-header'>
                <Typography variant="h5" style={{fontFamily: '"Times New Roman", serif'}}>{levelRomanNumeral}</Typography>
                {unlockedLevel == level - 1  && 
                    <Typography variant="h7"> ({myTechs}/{techsToUnlockNextLevel} to unlock) </Typography>
                }
            </div>
            {techs.map((tech) => (
                <TechCard key={tech.name} tech={tech} gameState={gameState} unitTemplates={unitTemplates} buildingTemplates={buildingTemplates} techTemplates={techTemplates} myCiv={myCiv} setHoveredTech={setHoveredTech} handleClickTech={handleClickTech}/>
            ))}
        </div>
    )
}

const TechCard = ({tech, gameState, techTemplates, unitTemplates, buildingTemplates, myCiv, setHoveredTech, handleClickTech}) => {
    return <div
        className={`tech-tree-card ${myCiv.techs_status[tech.name]} `}
        onMouseEnter={() => setHoveredTech(techTemplates[tech.name])}
        onMouseLeave={() => setHoveredTech(null)}
    onClick={() => myCiv.techs_status[tech.name] === 'available' && handleClickTech(tech)}

    >
        <div className="tech-tree-card-title">{tech.name}</div>
        <div className="tech-tree-card-effects">
            <div className="tech-tree-card-units">
                {tech.unlocks_units.map((unitName, index) => {
                    return <IconUnitDisplay
                        key={index}
                        unitName={unitName}
                        unitTemplates={unitTemplates}
                    ></IconUnitDisplay>
                })}
            </div>
            <div className="tech-tree-card-buildings">
                {tech.unlocks_buildings.map((buildingName, index) => {
                    return <BriefBuildingDisplay 
                        key={index} 
                        buildingName={buildingName} 
                        hideCost={true} 
                        buildingTemplates={buildingTemplates} 
                        setHoveredBuilding={()=>null}
                        disabledMsg={gameState.wonders_built_to_civ_id.hasOwnProperty(buildingName) ? `==  Built by ${gameState.civs_by_id[gameState.wonders_built_to_civ_id[buildingName]].name}  ==` : ""} 
                        style={{
                            fontSize: '0.8em',
                            borderColor: '#e46c2b',
                            height: '19px',
                            width: '100px',
                            padding: '0px 3px',
                            margin: "0px",
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            cursor: 'default'
                        }}
                    />
                })}
            </div>
        </div>
    </div>
}

const TechListDialog = ({open, onClose, setHoveredTech, handleClickTech, myCiv, gameState, techTemplates, unitTemplates, buildingTemplates}) => {
    if (!myCiv || !techTemplates) return null;
    
    const advancementLevels = Object.values(techTemplates).reduce((acc, tech) => {
        const level = tech.advancement_level;
        if (!acc[level]) {
            acc[level] = [];
        }
        acc[level].push(tech);
        return acc;
    }, {});

    const techLevelBox = (level) => {
        return <TechLevelBox level={level} techs={advancementLevels[level]} myCiv={myCiv} gameState={gameState} techTemplates={techTemplates} buildingTemplates={buildingTemplates} unitTemplates={unitTemplates} setHoveredTech={setHoveredTech} handleClickTech={handleClickTech}/>
    }

    return (
        <Dialog open={open} onClose={onClose} maxWidth="lg">
            <DialogTitle>
                <Typography variant="h5" component="div" style={{ flexGrow: 1, textAlign: 'center' }}>
                    All Technologies
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
                <img src={scienceImg} style={{
                        height: 'auto', 
                        width: '100px', 
                        position: "absolute",
                        left: "10px",
                        top: "10px",
                        }}/>
            </DialogTitle>
            <DialogContent className="tech-dialog-content">
                <TechColumn>
                    {techLevelBox(1)}
                </TechColumn>
                <TechColumn>
                    {techLevelBox(2)}
                    {techLevelBox(3)}
                </TechColumn>
                <TechColumn>
                    {techLevelBox(4)}
                    {techLevelBox(5)}
                    {techLevelBox(6)}
                </TechColumn>
                <TechColumn>                 
                    {techLevelBox(7)}
                    {techLevelBox(8)}
                    {techLevelBox(9)}
                </TechColumn>
            </DialogContent>
        </Dialog>
    )
}

export default TechListDialog;
