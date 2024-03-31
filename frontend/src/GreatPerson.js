import React from 'react';
import './GreatPerson.css';

const GreatPerson = ({greatPerson, handleSelectGreatPerson, setHoveredUnit, setHoveredTech, templates}) => {
    const handleMouseEnter = () => {
        if (greatPerson.hover_entity_type === "unit") {
            setHoveredUnit(templates.UNITS[greatPerson.hover_entity_name]);
        } else if (greatPerson.hover_entity_type === "tech") {
            setHoveredTech(templates.TECHS[greatPerson.hover_entity_name]);
        }
    }
    return (
        <div 
            className="great-person-card" 
            onClick={() => handleSelectGreatPerson(greatPerson)}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={() => {
                setHoveredUnit(null);
                setHoveredTech(null);
            }}
        >
            <h2>{greatPerson.name}</h2>
            <p>{greatPerson.description}</p>
        </div>
    )
}

export default GreatPerson;

