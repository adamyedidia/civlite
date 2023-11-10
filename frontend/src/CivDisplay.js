import React from 'react';
import './CivDisplay.css'; // Assuming you have a separate CSS file for styling

class CivDisplay extends React.Component {
    render() {
        const { name, abilities, primary_color, secondary_color } = this.props.civ;

        console.log(abilities);

        return (
            <div className="civ-card" style={{ borderColor: secondary_color }}>
                <div className="civ-card-inner" style={{ backgroundColor: primary_color }}>
                    <h2>{name}</h2>
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