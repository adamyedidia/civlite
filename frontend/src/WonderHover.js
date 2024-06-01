import React from 'react';
import './WonderHover.css';
import UnitDisplay from './UnitDisplay';
import { romanNumeral } from './TechListDialog';


const WonderHover = ({ wonder, templates}) => {
    return <div className={`wonder-card`}>
                <h2>{wonder.name}</h2>
                <div className="wonder-card-subtitle">
                <div>Age {romanNumeral(wonder.age)} Wonder</div>
                <div>{wonder.vp_reward} vp</div>
                </div>
                {wonder.description.map((desc, i) => <p key={i}>{desc}</p>)}
                {wonder.hover_unit_name && <UnitDisplay unit={templates.UNITS[wonder.hover_unit_name]} />}
            </div>
};

export default WonderHover;
