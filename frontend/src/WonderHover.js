import React from 'react';
import './WonderHover.css';
import UnitDisplay from './UnitDisplay';
import { romanNumeral } from './TechListDialog';
import woodImg from './images/wood.png';


const WonderHover = ({ wonder, templates}) => {
        return <div className={`wonder-card`}>
                <h2>{romanNumeral(wonder.advancement_level)}. {wonder.name}</h2>
                <div className="wonder-card-subtitle">
                <div>Age {romanNumeral(wonder.advancement_level)} Wonder</div>
                <div>{wonder.cost} <img src={woodImg} alt="wood" height="15px"/></div>
                </div>
                {wonder.description.map((desc, i) => <p key={i}>{desc}</p>)}
                {wonder.hover_unit_name && <UnitDisplay template={templates.UNITS[wonder.hover_unit_name]} />}
            </div>
};

export default WonderHover;
