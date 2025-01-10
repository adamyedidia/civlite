import React from 'react';
import './CivDisplay.css'; // Assuming you have a separate CSS file for styling
import { romanNumeral } from "./romanNumeral";
import { civNameToFlagSvgSrc } from './flag.js';

class CivDisplay extends React.Component {

    render() {
        const { civ, templates } = this.props

        const { vitality, name } = civ;
        const { abilities, primary_color, secondary_color, advancement_level, darkmode } = templates.CIVS[name];

        const hoveredGamePlayerDisplay = this.props?.hoveredGamePlayer ? ` (${this.props.hoveredGamePlayer})` : '';

        const vitalityDisplay = (vitality && name !== 'Barbarians') ? `Vitality: ${Math.floor(vitality * 100)}%` : null;

        return (
            <div className="civ-card" style={{ borderColor: secondary_color }}>
                <div className="civ-card-inner" style={{ backgroundColor: primary_color }}>
                    <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                        <img 
                            src={civNameToFlagSvgSrc(name)} 
                            alt={`${name} flag`} 
                            className="civ-flag"
                            style={{ 
                                width: '200px',
                                filter: darkmode ? 
                                    'drop-shadow(0 0 2px white) drop-shadow(0 0 2px white)' : 
                                    'drop-shadow(0 0 2px black) drop-shadow(0 0 2px black)',
                            }} 
                        />    
                    </div>
                    <h2 style={{color: darkmode ? "white" : "black"}}>{`${name} ${hoveredGamePlayerDisplay}`}</h2>
                    <h4 style={{color: darkmode ? "white" : "black"}}>{`Age ${romanNumeral(advancement_level)} civilization`}</h4>
                    {vitalityDisplay && <h4 style={{color: darkmode ? "white" : "black"}}>{vitalityDisplay}</h4>}
                    <ul>
                        {abilities.map((ability, index) => (
                            <li key={index} style={{color: darkmode ? "white" : "black"}}>{ability.description}</li>
                        ))}
                    </ul>
                </div>
            </div>
        );
    }
}

export default CivDisplay;