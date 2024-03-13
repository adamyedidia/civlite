import React from 'react';
import './CivDisplay.css'; // Assuming you have a separate CSS file for styling

class CivDisplay extends React.Component {
    render() {
        const { civ, civTemplates } = this.props

        const { vitality, name } = civ;
        const { abilities, primary_color, secondary_color } = civTemplates[name];

        const hoveredGamePlayerDisplay = this.props?.hoveredGamePlayer ? ` (${this.props.hoveredGamePlayer})` : '';

        const vitalityDisplay = (vitality && name !== 'Barbarians') ? `Vitality: ${Math.floor(vitality * 100)}%` : null;

        return (
            <div className="civ-card" style={{ borderColor: secondary_color }}>
                <div className="civ-card-inner" style={{ backgroundColor: primary_color }}>
                    <h2>{`${name} ${hoveredGamePlayerDisplay}`}</h2>
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