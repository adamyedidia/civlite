import React from 'react';
import './WonderHover.css';
import UnitDisplay from './UnitDisplay';


const WonderHover = ({ wonder, templates}) => {
    return <div className={`wonder-card`}>
                <h2>{wonder.name}</h2>
                <p>{wonder.vp_reward} vp</p>
                <p>{wonder.description}</p>
                {<UnitDisplay unit={templates.UNITS[wonder.hover_unit_name]} />}
            </div>
};

export default WonderHover;
