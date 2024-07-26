import React, { useState } from 'react';
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
    Select,
    MenuItem,
} from '@mui/material';
import { ShrinkFontText } from './ShrinkFontText.js';
import { romanNumeral } from './TechListDialog.js';

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

const UnitDisplay = ({ template, unit }) => {
    if (!template) {
        if (!unit) {
            return null;
        }
        template = unit.template;
    }

    const strength = unit ? unit.strength : template.strength;
    const shieldSize = strength >= 100 ? 80 : strength >= 10 ? 60 : 40;
    const tags = template.tags;
    const displayTags = tags.filter(tag => tag !== "gunpowder").sort();
    return (
        <div className="unit-card">
            <h2>{romanNumeral(template.advancement_level)}. {template.name}</h2>
            <div className="subtitle-row">
                <div className="cost-row">
                    <div className="cost" style={template.building_name ? {visibility: 'visible'} : {visibility: 'hidden'}}>
                        <div className="cost-itself">{template.wood_cost} <img src={woodImg} alt="" width="auto" height="12" /></div>
                        <ShrinkFontText text={template.building_name} startFontSize={16}/> 
                    </div>
                    <div className="cost">
                        <div className="cost-itself">{template.metal_cost} <img src={metalImg} alt="" width="auto" height="12" /></div>
                        <ShrinkFontText text={template.name} startFontSize={16}/>
                    </div>
                </div>
                <div className="tags">
                    {displayTags.map((tag, i) => (
                        <div key={i} className="tag">{tag}</div>
                    ))}
                </div>
            </div>
            <div className="content">
                <div className="abilities">
                    {template.abilities.map((ability) => (
                        <p key={ability.name}>{ability.description}</p>
                    ))}
                </div>
            </div>
            <div className="stats">
                <div className="stat move">
                    {template.movement > 0 ? `Move: ${template.movement}` : 'IMMOBILE'}
                </div>
                {strength !== template.strength && <div className='base-strength'></div>} {/* So that the big one stays in the center */}
                <TextOnIcon image={shieldImg} style={{ height: `${shieldSize}px`, width: `${shieldSize}px` }} offset={-shieldSize * 0.15}>
                    <span className='strength-text'>{strength}</span>
                </TextOnIcon>
                {strength !== template.strength && <div className='base-strength'>
                    <span style={{fontSize: '0.5em'}}>Base</span>
                    <TextOnIcon image={shieldImg} style={{ height: `${shieldSize * 0.67}px`, width: `${shieldSize * 0.67}px` }} offset={-shieldSize * 0.1}>
                        <span className='strength-text small'>{template.strength}</span>
                    </TextOnIcon>
                </div>}
                <div className="stat range">
                    {tags.includes('ranged') ? `Range: ${template.range}` : "Melee"}
                </div>
            </div>
        </div>
    );
};

export const AllUnitsDialog = ({ units, open, onClose }) => {
    const [sortBy, setSortBy] = useState("name");
    const sort_fn = (a) => 
        a.tags.includes("wondrous") * 100
        + (sortBy === "age") * (a.advancement_level + 0.01 * a.metal_cost)
        + (sortBy === "strength") * (a.strength)
    const sortedUnits = Object.values(units).sort((a, b) => sort_fn(a) - sort_fn(b) + 0.01 * (a.name.localeCompare(b.name)));
    return <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
        <DialogTitle>
            <Typography variant="h5" component="div" style={{ textAlign: 'center' }}>
                All Units
            </Typography>
            <Select value={sortBy} onChange={(e) => setSortBy(e.target.value)} style={{
                    position: 'absolute',
                    left: 30,
                    top: 8,
                }}>
                <MenuItem value="name">A-Z</MenuItem>
                <MenuItem value="age">Age</MenuItem>
                <MenuItem value="strength">Strength</MenuItem>
            </Select>
            <IconButton
                aria-label="close"
                onClick={onClose}
                style={{
                    position: 'absolute',
                    right: 30,
                    top: 8,
                    color: (theme) => theme.palette.grey[500],
                }}
                color="primary"
            >
                Close
            </IconButton>
        </DialogTitle>
        <div className="all-units-display">
            {sortedUnits.map((unit, i) => <UnitDisplay key={i} template={unit} width="100"/>)}
        </div>
    </Dialog>
};

export default UnitDisplay;