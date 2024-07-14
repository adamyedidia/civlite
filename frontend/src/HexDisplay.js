import React from 'react';
import UnitDisplay from './UnitDisplay'; // Adjust the path as needed
import './HexDisplay.css'; // Assuming you have a separate CSS file for styling

import foodImg from './images/food.png';
import woodImg from './images/wood.png';
import metalImg from './images/metal.png';
import scienceImg from './images/science.png';

export const YieldImages = ({ yields }) => {
    let imageCounter = 0; // Counter to track the total number of images

    if (!yields) {
        return null;
    }

    let totalCount = yields.food + yields.wood + yields.metal + yields.science;

    const renderImages = (img, count) => {
        let images = [];
        for (let i = 0; i < count; i++) {
            images.push(
                <image 
                    key={`${img}-${imageCounter}`} 
                    href={img} 
                    x={totalCount > 1 ? 1.5 / 0.7 * (imageCounter / (totalCount - 1) + 0.1 / totalCount - 1) : -1} 
                    y={-1} 
                    height={2} 
                    width={2}
                />
            );
            imageCounter++; // Increment counter for each image
        }
        return images;
    };

    return (
        <g>
            {renderImages(foodImg, yields.food)}
            {renderImages(woodImg, yields.wood)}
            {renderImages(metalImg, yields.metal)}
            {renderImages(scienceImg, yields.science)}
        </g>
    );
};


export const YieldImages2 = ({ yields }) => {
    if (!yields) {
        return null;
    }

    const renderImages = (img, count) => {
        let images = [];
        for (let i = 0; i < count; i++) {
            images.push(
                <img 
                    key={`${img}-${i}`} 
                    src={img} 
                    alt="yield"
                    style={{ width: '20px', height: '20px' }} // Adjust size as needed
                />
            );
        }
        return images;
    };

    return (
        <div style={{ display: 'flex', gap: '5px' }}>
            {renderImages(foodImg, yields.food)}
            {renderImages(woodImg, yields.wood)}
            {renderImages(metalImg, yields.metal)}
            {renderImages(scienceImg, yields.science)}
        </div>
    );
};


const HexDisplay = ({ hoveredHex, templates }) => {
    if (!hoveredHex) {
        return null;
    }

    return (
        <div className="hex-display">
            <h3>Hex Info</h3>
            {hoveredHex.yields && <YieldImages2 yields={hoveredHex.yields} />}
            {hoveredHex.terrain && <p>Terrain: {hoveredHex.terrain}</p>}
            {hoveredHex.city && <p>City: {hoveredHex.city.name} ({hoveredHex.city.population})</p>}
            <div className="hex-units">
                {hoveredHex.units && hoveredHex.units.map((unit, index) => (
                    <UnitDisplay key={index} template={templates.UNITS[unit]} />
                ))}
            </div>
            {`${hoveredHex.q}, ${hoveredHex.r}, ${hoveredHex.s}`}
        </div>
    );
};

export default HexDisplay;