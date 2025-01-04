import React from 'react';
import './CivDisplay.css'; // Assuming you have a separate CSS file for styling
import { romanNumeral } from "./romanNumeral";
import { civNameToFlagImgSrc } from './flag.js';

class CivDisplay extends React.Component {

    render() {
        const { civ, templates } = this.props

        const { vitality, name } = civ;
        const { abilities, primary_color, secondary_color, advancement_level } = templates.CIVS[name];

        const hoveredGamePlayerDisplay = this.props?.hoveredGamePlayer ? ` (${this.props.hoveredGamePlayer})` : '';

        const vitalityDisplay = (vitality && name !== 'Barbarians') ? `Vitality: ${Math.floor(vitality * 100)}%` : null;

        return (
            <div className="civ-card" style={{ borderColor: secondary_color }}>
                <div className="civ-card-inner" style={{ backgroundColor: primary_color }}>
                    <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                        <img 
                            src={civNameToFlagImgSrc(name)} 
                            alt={`${name} flag`} 
                            className="civ-flag"
                            style={{ width: '200px' }} // Adjust size as needed
                        />            
                    </div>
                    <h2>{`${name} ${hoveredGamePlayerDisplay}`}</h2>
                    <h4>{`Age ${romanNumeral(advancement_level)} civilization`}</h4>
                    {vitalityDisplay && <h4>{vitalityDisplay}</h4>}
                    <ul>
                        {abilities.map((ability, index) => (
                            <li key={index}>{ability.description}</li>
                        ))}
                    </ul>
                </div>
            </div>
        );
    }
}

export default CivDisplay;