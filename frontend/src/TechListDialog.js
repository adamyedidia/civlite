import React from "react";
import './TechListDialog.css';

import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Typography } from "@mui/material";
import { IconUnitDisplay } from "./UnitDisplay";

const TechColumn = ({children}) => {
    return <div className="tech-column">{children}</div>
}

const TechLevelBox = ({level, techs, myCiv, techTemplates, unitTemplates, setHoveredTech}) => {
    const levelRomanNumeral = level === 1 ? 'I' : level === 2 ? 'II' : level === 3 ? 'III' : level === 4 ? 'IV' : level === 5 ? 'V' : level === 6 ? 'VI' : level === 7 ? 'VII' : level === 8 ? 'VIII' : level === 9 ? 'IX' : level === 10 ? 'X' : level === 11 ? 'XI' : level === 12 ? 'XII' : level === 13 ? 'XIII' : '???';

    // Need to keep this in sync with python code. Might be better to pass it down.
    const myTechs = Object.keys(myCiv.techs).length;
    const unlockedLevel = Math.max(1, Math.floor(myTechs / 3));
    const techsToUnlockNextLevel = unlockedLevel > 1 ? 3 * (unlockedLevel + 1) : 6;
    return (
        <div className={`tech-level-box ${unlockedLevel < level ? 'disabled' : ''}`}>
            <div className='tech-level-box-header'>
                <Typography variant="h5" style={{fontFamily: '"Times New Roman", serif'}}>{levelRomanNumeral}</Typography>
                {unlockedLevel == level - 1  && 
                    <Typography variant="h5"> ({myTechs}/{techsToUnlockNextLevel} to unlock) </Typography>
                }
            </div>
            {techs.map((tech) => (
                <TechCard key={tech.name} tech={tech} unitTemplates={unitTemplates} techTemplates={techTemplates} myCiv={myCiv} setHoveredTech={setHoveredTech}/>
            ))}
        </div>
    )
}

const TechCard = ({tech, techTemplates, unitTemplates, myCiv, setHoveredTech}) => {
    return <div
        className={`tech-tree-card ${myCiv.techs[tech.name] ? 'researched' : myCiv.tech_queue?.[0].name === tech.name ? 'researching' : ''} `}
        onMouseEnter={() => setHoveredTech(techTemplates[tech.name])}
        onMouseLeave={() => setHoveredTech(null)}
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
            <div className="tech-card-buildings">
                {tech.unlocks_buildings.map((buildingName, index) => {
                    return <div 
                        key={index}
                        className="tech-tree-card-building"
                        >
                        {buildingName}
                        </div>
                })}
            </div>
        </div>
    </div>
}

const TechListDialog = ({open, onClose, setHoveredTech, myCiv, techTemplates, unitTemplates}) => {
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
        return <TechLevelBox level={level} techs={advancementLevels[level]} myCiv={myCiv} techTemplates={techTemplates} unitTemplates={unitTemplates} setHoveredTech={setHoveredTech}/>
    }

    return (
        // TODO(dfarhi) Make it wider
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>All Technologies</DialogTitle>
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
                    {techLevelBox(10)}
                </TechColumn>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Close
                </Button>
            </DialogActions>
        </Dialog>
    )
}

export default TechListDialog;
