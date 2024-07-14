import React from 'react';
import './UnitDisplay.css'; // Assuming you have a separate CSS file for styling
import { lowercaseAndReplaceSpacesWithUnderscores } from './lowercaseAndReplaceSpacesWithUnderscores.js';
import woodImg from './images/wood.png';
import metalImg from './images/metal.png';
import shieldImg from './images/shield.png';
import { TextOnIcon } from './TextOnIcon.js';
import { 
    Dialog, 
    DialogTitle, 
    Typography, 
    IconButton,
} from '@mui/material';
import { ShrinkFontText } from './ShrinkFontText.js';

export const BriefUnitDisplayTitle = ({ title }) => {
    return (
        <div 
            className="unit-title-card" 
        >
            <span className="unit-name">{title}</span>
        </div>        
    );
}

export const BriefUnitDisplay = ({ unitName, templates, onClick, setHoveredUnit }) => {
    const unit = templates.UNITS[unitName]

    return (
        <div 
            className="brief-unit-card" 
            onClick={onClick}
            onMouseEnter={() => setHoveredUnit(unit)} // set on mouse enter
            onMouseLeave={() => setHoveredUnit(null)} // clear on mouse leave
        >
            <span className="unit-name">{unit?.name}</span>
            <span className="unit-cost">{unit?.metal_cost} metal</span>
        </div>
    );
};

export const IconUnitDisplay = ({ unitName, templates, style, onClick, setHoveredUnit, size }) => {
    size = (size || 40) + "px";
    let unit;
    if (unitName) {
        unit = templates.UNITS[unitName];
        const unitImage = `/images/${lowercaseAndReplaceSpacesWithUnderscores(unit.name)}.svg`; // Path to the unit SVG image
        style = { ...style, height: size, width: size, backgroundImage: `url(${unitImage})`}
    }
    return (
        <div 
            className="unit-icon" 
            onClick={onClick}
            onMouseEnter={() => setHoveredUnit && unit && setHoveredUnit(unit)} // set on mouse enter
            onMouseLeave={() => setHoveredUnit && setHoveredUnit(null)} // clear on mouse leave
            style={style}
        />
    );
};

const UnitDisplay = ({ unit }) => {
    if (!unit) {
        return null;
    }

    const unitAbilities = unit?.abilities?.length > 0 ? unit.abilities : unit?.template?.abilities

    const shieldSize = unit.strength >= 100 ? 80 : unit.strength >= 10 ? 60 : 40;
    const displayTags = unit.tags.filter(tag => tag !== "gunpowder").sort();
    return (
        <div className="unit-card">
            <h2>{unit?.name || unit?.template?.name}</h2>
            <div className="cost-row">
                <div className="cost" style={unit.building_name ? {visibility: 'visible'} : {visibility: 'hidden'}}>
                    <ShrinkFontText text={unit.building_name + ":"} startFontSize={16}/> 
                    <div className="cost-itself">{unit.wood_cost} <img src={woodImg} alt="" width="auto" height="12" /></div>
                </div>
                <div className="cost">
                   <ShrinkFontText text={unit.name + ":"} startFontSize={16}/>
                   <div className="cost-itself">{unit.metal_cost} <img src={metalImg} alt="" width="auto" height="12" /></div>
                </div>
            </div>
            <div className="content">
                <div className="tags">
                    {displayTags.join(', ')}
                </div>
                <div className="abilities">
                    {unitAbilities?.map((ability) => (
                        <p key={ability.name}>{ability.description}</p>
                    ))}
                </div>
            </div>
            <div className="stats">
                <div>
                    {unit.movement > 0 ? `Move: ${unit.movement}` : 'IMMOBILE'}
                </div>
                <TextOnIcon image={shieldImg} style={{ height: `${shieldSize}px`, width: `${shieldSize}px` }} offset={-shieldSize * 0.15}>
                    <span className='strength-text'>{unit.strength}</span>
                </TextOnIcon>
                <div>
                    {unit.tags.includes('ranged') ? `Range: ${unit.range}` : "Melee"}
                </div>
            </div>
        </div>
    );
};

export const AllUnitsDialog = ({ units, open, onClose }) => {
    return <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
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
        </DialogTitle>
        <div className="all-units-display">
            {Object.values(units).sort(
                (a, b) => (a.tags.includes("wondrous") - b.tags.includes("wondrous")) * 100 + a.name.localeCompare(b.name)
            ).map((unit, i) => <UnitDisplay key={i} unit={unit} width="100"/>)}
        </div>
    </Dialog>
};

export default UnitDisplay;