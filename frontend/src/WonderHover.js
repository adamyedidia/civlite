import React from 'react';
import './WonderHover.css';


const WonderHover = ({ wonder, }) => {
    console.log(wonder)
    return <div className={`wonder-card`}>
                <h2>{wonder.name}</h2>
            </div>
};

export default WonderHover;
