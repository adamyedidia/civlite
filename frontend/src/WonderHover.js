import React from 'react';
import './WonderHover.css';


const WonderHover = ({ wonder, }) => {
    console.log(wonder)
    return <div className={`wonder-card`}>
                <h2>{wonder.name}</h2>
                <p>{wonder.vp_reward} vp</p>
                <p>{wonder.description}</p>
            </div>
};

export default WonderHover;
