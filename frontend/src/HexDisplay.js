import React from 'react';
import UnitDisplay from './UnitDisplay'; // Adjust the path as needed
import './HexDisplay.css'; // Assuming you have a separate CSS file for styling

import foodImg from './images/food.png';
import woodImg from './images/wood.png';
import metalImg from './images/metal.png';
import scienceImg from './images/science.png';
import smallBldgImg from './images/smallbldg.png';
import largeBldgImg from './images/largebldg.png';

import { shuffle } from 'lodash';

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

export const HexBuffIcons = ({ buff_counts, hex_based_seed }) => {
    const BLDG_LOCATIONS = [
        {x: -2, y: -2},
        {x: -0.8, y: -2.4},
        {x: 0.3, y: -2.4},
        {x: 0.8, y: -1.9},
        {x: 1.7, y: -0.3},
        {x: 1.4, y: 0.3},
        {x: 1.1, y: 1.2},
        {x: 0, y: 0.9},
        {x: -0.6, y: 1.5},
        {x: -1.5, y: 1.5},
        {x: -2.0, y: 1.0},
        {x: -2.8, y: -0.5},
    ];
    // shuffle them
    BLDG_LOCATIONS.sort((a, b) => (Math.sin(a.x * hex_based_seed * 1000) - Math.sin(b.x * hex_based_seed * 1000)));

    let imageCounter = 0; // Counter to track the total number of images
    const renderImages = (img, count) => {
        let images = [];
        for (let i = 0; i < count && imageCounter < BLDG_LOCATIONS.length; i++) {
            images.push(
                <image 
                    key={`${img}-${imageCounter}`} 
                    href={img} 
                    x={BLDG_LOCATIONS[imageCounter].x}
                    y={BLDG_LOCATIONS[imageCounter].y}
                    height={1} 
                    width={1}
                />
            );
            imageCounter++; // Increment counter for each image
        }
        images.sort((a, b) => a.props.y - b.props.y);
        return images;
    };

    return (
        <g>
            {renderImages(smallBldgImg, buff_counts.small)}
            {renderImages(largeBldgImg, buff_counts.large)}
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
                    <UnitDisplay key={index} unit={templates.UNITS[unit]} />
                ))}
            </div>
            {`${hoveredHex.q}, ${hoveredHex.r}, ${hoveredHex.s}`}
        </div>
    );
};

export default HexDisplay;