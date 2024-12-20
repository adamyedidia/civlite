import React from "react";
import './TechListDialog.css';

import { Dialog, DialogTitle, DialogContent, Typography, IconButton } from "@mui/material";
import { IconUnitDisplay } from "./UnitDisplay";
import { BriefBuildingDisplay } from "./BuildingDisplay";
import scienceImg from './images/science.png';
import fountainImg from './images/fountain.svg';
import ProgressBar from "./ProgressBar";
import { romanNumeral } from "./romanNumeral";

const TechColumn = ({children}) => {
    return <div className="tech-column">{children}</div>
}

const TechLevelBox = ({level, techs, myCiv, myGamePlayer, gameState, templates, setHoveredTech, handleClickTech}) => {
    const levelRomanNumeral = romanNumeral(level);

    const nextAgeProgress = myCiv.next_age_progress;
    const unlockedLevel = myCiv.advancement_level;
    const researchingTechName = myCiv.researching_tech_name;
    const reserachingTechLevel = (researchingTechName && researchingTechName != "Renaissance") ? templates.TECHS[researchingTechName].advancement_level : 0;
    const fountainTechs = myGamePlayer.tenets["Fountain of Youth"]?.unclaimed_techs;
    return (
        <div className={`tech-level-box ${unlockedLevel < level ? 'disabled' : ''}`}>
            <div className='tech-level-box-header'>
                <Typography variant="h5" style={{fontFamily: '"Times New Roman", serif'}}>{levelRomanNumeral}</Typography>
                {unlockedLevel === level - 1  && 
                    <ProgressBar barText={`${nextAgeProgress.partial}/${nextAgeProgress.needed} lvls`} darkPercent={100 * nextAgeProgress.partial/nextAgeProgress.needed} lightPercent={100 * reserachingTechLevel/nextAgeProgress.needed}/>
                }
            </div>
            {techs.map((tech) => (
                <TechCard key={tech.name} tech={tech} gameState={gameState} templates={templates} myCiv={myCiv} 
                setHoveredTech={setHoveredTech} handleClickTech={handleClickTech} fountainIcon={fountainTechs?.includes(tech.name)}/>
            ))}
        </div>
    )
}

const TechCard = ({tech, gameState, templates, myCiv, setHoveredTech, handleClickTech, fountainIcon}) => {
    return <div
        className={`tech-tree-card ${myCiv.techs_status[tech.name]} `}
        onMouseEnter={() => setHoveredTech(templates.TECHS[tech.name])}
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
                        templates={templates}
                    ></IconUnitDisplay>
                })}
            </div>
            <div className="tech-tree-card-buildings">
                {tech.unlocks_buildings.map((buildingName, index) => {
                    return <BriefBuildingDisplay 
                        key={index} 
                        buildingName={buildingName}
                        clickable={false}
                        hideCost={true} 
                        templates={templates} 
                        setHoveredBuilding={()=>null}
                        style={{
                            fontSize: '0.8em',
                            borderColor: '#e46c2b',
                            height: '19px',
                            width: '100px',
                            padding: '0px 3px',
                            margin: "0px",
                            whiteSpace: 'nowrap',
                            overflow: 'hidden',
                            cursor: 'default',
                            flexGrow: '0',
                        }}
                    />
                })}
            </div>
        </div>
        {fountainIcon && <img src={fountainImg} className="fountain-icon"/>}
    </div>
}

const TechListDialog = ({open, onClose, setHoveredTech, handleClickTech, myCiv, myGamePlayer, gameState, templates}) => {
    if (!myCiv || !templates) return null;
    
    const advancementLevels = Object.values(templates.TECHS).reduce((acc, tech) => {
        const level = tech.advancement_level;
        if (!acc[level]) {
            acc[level] = [];
        }
        acc[level].push(tech);
        return acc;
    }, {});

    const techLevelBox = (level) => {
        return <TechLevelBox level={level} techs={advancementLevels[level]} myCiv={myCiv} myGamePlayer={myGamePlayer} gameState={gameState} templates={templates} setHoveredTech={setHoveredTech} handleClickTech={handleClickTech}/>
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
                <img src={scienceImg} alt="" style={{
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
