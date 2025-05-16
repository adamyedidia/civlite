import { useState, useEffect } from 'react';

import knightSpriteData from './MiniCavalierMan.js';
// import garrisonSpriteData from './MiniSwordMan.js';
import horsemanSpriteData from './MiniHorseMan.js';
import swordsmanSpriteData from './MiniShieldMan.js';
import archerSpriteData from './MiniArcherMan.js';
import crossbowmanSpriteData from './MiniCrossBowMan.js';
import spearmanSpriteData from './MiniSpearMan.js';
import pikemanSpriteData from './MiniHalberdMan.js';
import cannonSpriteData from './MiniCannon.js';
import musketmanSpriteData from './MiniPirateGunner.js';

import { lowercaseAndReplaceSpacesWithUnderscores } from './lowercaseAndReplaceSpacesWithUnderscores.js';
import { civNameToShieldImgSrc } from './flag.js';
import { useGlobalClockValue } from './GlobalClockContext.js';
const BasicUnit = ({ unit, small, templates, civsById }) => {
    const unitCivTemplate = templates.CIVS[civsById?.[unit.civ_id]?.name]

    const primaryColor = unitCivTemplate?.primary_color;
    const secondaryColor = unitCivTemplate?.secondary_color;
    const unitImage = `/images/${lowercaseAndReplaceSpacesWithUnderscores(unit.name)}.svg`; // Path to the unit SVG image

    const scale = small ? 0.95 : 1.4;
    let healthPercentage = (unit.health / 100) % 1; // Calculate health as a percentage
    if (healthPercentage === 0) {
        healthPercentage = 1;
    }

    const buffedUnit = unit.strength - templates.UNITS[unit.name].strength;
    let buffIconIndex
    if (templates.UNITS[unit.name].advancement_level <= 3) {
        buffIconIndex = buffedUnit;
    } else {
        buffIconIndex = Math.ceil(buffedUnit / (0.25 * templates.UNITS[unit.name].strength))
    }
    const buffIcons = ['+', "▲", "★", "✸"];
    const buffIcon = buffIconIndex < buffIcons.length ? buffIcons[buffIconIndex - 1] : buffIcons[buffIcons.length - 1];
    return (
        <svg width={`${4*scale}`} height={`${4*scale}`} viewBox={`0 0 ${4*scale} ${4*scale}`} x={-2*scale} y={-2*scale + (small ? 1 : 0)}>
            <circle opacity={unit.done_attacking ? 0.5 : 1.0} cx={`${2*scale}`} cy={`${2*scale}`} r={`${scale}`} fill={primaryColor} stroke={secondaryColor} strokeWidth={0.3} />
            {buffedUnit > 0 && <circle opacity={unit.done_attacking ? 0.5 : 1.0} cx={`${1*scale}`} cy={`${3*scale}`} r={`${0.4 * scale}`} fill={primaryColor} stroke={secondaryColor} strokeWidth={0.15} />}
            {buffedUnit > 0 && <text opacity={unit.done_attacking ? 0.5 : 1.0} x={`${1*scale}`} y={`${3*scale}`} style={{ fontSize: `${scale * 0.5}px`, textAnchor: "middle", dominantBaseline: "middle", fill: unitCivTemplate?.darkmode ? "white" : "black" }}> {buffIcon} </text>}
            <image 
                href={unitImage} 
                x={`${scale}`} 
                y={`${scale}`} 
                height={`${2*scale}`} 
                width={`${2*scale}`}
                style={{
                    filter: unitCivTemplate?.darkmode ? 'invert(1)' : 'none'
                }}
            />
            <rect x={`${scale}`} y={`${3.4*scale}`} width={`${2*scale}`} height={`${0.2*scale}`} fill="#ff0000" /> {/* Total health bar */}
            <rect x={`${scale}`} y={`${3.4*scale}`} width={`${2*scale*healthPercentage}`} height={`${0.2*scale}`} fill="#00ff00" /> {/* Current health bar */}
            {unit.stack_size > 1 && <circle cx={`${2*scale + 0.8*scale}`} cy={`${3.5*scale - 0.8*scale}`} r={`${scale/2}`} fill="white" stroke="black" strokeWidth={0.1} style={{ zIndex: 99999 }} />}
            {unit.stack_size > 1 && <text x={`${2.8*scale}`} y={`${2.8*scale}`} style={{ fontSize: `${scale}px`, textAnchor: "middle", dominantBaseline: "middle", zIndex: 99999 }}>{unit.stack_size}</text>}
        </svg>
    );
};

export function UnitCorpse({ corpse, small, templates, civsById }) {
    const clock = useGlobalClockValue();
    const unitCivTemplate = templates.CIVS[civsById?.[corpse.unit_civ_id]?.name]
    const primaryColor = unitCivTemplate?.primary_color;
    const secondaryColor = unitCivTemplate?.secondary_color;

    const [deathStartTime, setDeathStartTime] = useState(null);

    useEffect(() => {
        setDeathStartTime(clock);
    }, []);

    const spriteData = {
        // "Garrison": garrisonSpriteData,
        "Horseman": horsemanSpriteData,
        "Knight": knightSpriteData,
        "Swordsman": swordsmanSpriteData,
        "Archer": archerSpriteData,
        "Crossbowman": crossbowmanSpriteData,
        "Spearman": spearmanSpriteData,
        "Pikeman": pikemanSpriteData,
        "Cannon": cannonSpriteData,
        "Musketman": musketmanSpriteData,
    }[corpse.unit_name];

    if (spriteData) {
        const scale = small ? 0.95 : 1.4;
        const pixelSize = scale * 4/16; // 4 units total width / 16 pixels

        const framesSinceAttackStart = clock - deathStartTime;
        const currentFrame = framesSinceAttackStart;

        if (currentFrame >= spriteData.die.length) {
            return null;
        }

        const currentFrameData = spriteData.die[currentFrame];

        const frameWidth = currentFrameData[0]?.length || 16;
        const frameHeight = currentFrameData.length || 16;
        
        // Calculate centering offsets
        const horizontalOffset = (16 - frameWidth) / 2 * pixelSize;  // Assuming 16 is our target width
        const verticalOffset = (16 - frameHeight) * pixelSize + scale;  // -scale for general adjustment

        return (
            <svg 
                width={`${4*scale}`} 
                height={`${4*scale}`} 
                viewBox={`0 0 ${4*scale} ${6*scale}`}
                x={-2*scale} 
                y={-2*scale + (small ? 1 : 0)}
                opacity={1.0}
            >
                <g transform={`translate(${horizontalOffset}, ${verticalOffset})`}>
                    {spriteData.die[currentFrame].map((row, y) => 
                        row.map((pixel, x) => {
                            if (Array.isArray(pixel) && pixel[3] === 0) return null;
                            
                            let color;
                            if (pixel === "team color 1") {
                                color = primaryColor;
                            } else if (pixel === "team color 2") {
                                color = secondaryColor;
                            } else {
                                color = `rgba(${pixel[0]}, ${pixel[1]}, ${pixel[2]}, ${pixel[3]/255})`;
                            }
    
                            return (
                                <rect
                                    key={`${x}-${y}`}
                                    x={Math.round(x * pixelSize * 100) / 100}
                                    y={Math.round(y * pixelSize * 100) / 100}
                                    width={Math.round(pixelSize * 100) / 100}
                                    height={Math.round(pixelSize * 100) / 100}
                                    fill={color}
                                />
                            );
                        })
                    )}
                </g> 
            </svg>
        );
    }

    return null;

}

export default function Unit({ unit, small, templates, civsById, attackingUnitCoords, attackedUnitCoords }) {
    const clock = useGlobalClockValue();
    const unitCivTemplate = templates.CIVS[civsById?.[unit.civ_id]?.name]
    const primaryColor = unitCivTemplate?.primary_color;
    const secondaryColor = unitCivTemplate?.secondary_color;

    const civName = unitCivTemplate?.name;

    const [isAttacking, setIsAttacking] = useState(false);
    const [isAttacked, setIsAttacked] = useState(false);
    const [attackStartTime, setAttackStartTime] = useState(null);
    const [animationComplete, setAnimationComplete] = useState(false);

    const spriteData = {
        // "Garrison": garrisonSpriteData,
        // "Horseman": horsemanSpriteData,
        // "Knight": knightSpriteData,
        // "Swordsman": swordsmanSpriteData,
        // "Archer": archerSpriteData,
        // "Crossbowman": crossbowmanSpriteData,
        // "Spearman": spearmanSpriteData,
        // "Pikeman": pikemanSpriteData,
        // "Cannon": cannonSpriteData,
        // "Musketman": musketmanSpriteData,
    }[unit.name];

    // Check if this unit is the attacker and manage attack animation
    useEffect(() => {
        if (unit.hex === attackingUnitCoords && !isAttacking) {
            setIsAttacking(true);
            setAttackStartTime(clock);
            setAnimationComplete(false);
        }
        if (unit.hex === attackedUnitCoords && !isAttacked) {
            setIsAttacked(true);
            setAttackStartTime(clock);
            setAnimationComplete(false);
        }
        if (unit.hex !== attackingUnitCoords && (isAttacking || isAttacked) && animationComplete) {
            setIsAttacking(false);
            setIsAttacked(false);
        }
        const currentAnimation = isAttacking ? 'attack' : 'ouch';

        const framesSinceAttackStart = clock - attackStartTime;
        if (spriteData && framesSinceAttackStart >= spriteData?.[currentAnimation]?.length) {
            setAnimationComplete(true);
        }
    }, [attackingUnitCoords, attackedUnitCoords, unit.hex, isAttacking, isAttacked, animationComplete, clock]);

    // Set up animation loop
    // useEffect(() => {
    //     if (!spriteData) return;
        
    //     const frameInterval = setInterval(() => {
    //         // setCurrentFrame(prev => (prev + 1) % spriteData.idle.length);
    //         setCurrentFrame(prev => clock % spriteData.idle.length);
    //     }, 150); // Adjust timing as needed (150ms = ~6.6fps)

    //     return () => clearInterval(frameInterval);
    // }, []);


    // const currentFrame = !!spriteData ? Math.floor(clock / 150) % spriteData.idle.length : 0;

    if (spriteData) {

        const scale = small ? 0.95 : 1.4;
        const pixelSize = scale * 4/16; // 4 units total width / 16 pixels

        // Determine which animation to use and which frame to show
        let currentAnimation = 'idle';
        let currentFrame = 0;

        if (isAttacking) {
            const framesSinceAttackStart = clock - attackStartTime;
            if (framesSinceAttackStart) {
                // Still playing attack animation
                currentAnimation = 'attack';
                currentFrame = framesSinceAttackStart % spriteData.attack.length;
            } 
        } else if (isAttacked) {
            const framesSinceAttackStart = clock - attackStartTime;
            if (framesSinceAttackStart) {
                // Still playing attack animation
                currentAnimation = 'ouch';
                currentFrame = framesSinceAttackStart % spriteData.ouch.length;
            } 
        } else {
            // Normal idle animation
            currentAnimation = 'idle';
            currentFrame = Math.floor(clock / 2) % spriteData.idle.length;
        }

        const currentFrameData = spriteData[currentAnimation][currentFrame];

        const frameWidth = currentFrameData[0]?.length || 16;
        const frameHeight = currentFrameData.length || 16;
        
        let healthPercentage = (unit.health / 100) % 1; // Calculate health as a percentage
        if (healthPercentage === 0) {
            healthPercentage = 1;
        }

        // Calculate centering offsets
        const horizontalOffset = (16 - frameWidth) / 2 * pixelSize;  // Assuming 16 is our target width
        const verticalOffset = (16 - frameHeight) * pixelSize + scale;  // -scale for general adjustment
        
        const buffedUnit = unit.strength - templates.UNITS[unit.name].strength;
        let buffIconIndex
        if (templates.UNITS[unit.name].advancement_level <= 3) {
            buffIconIndex = buffedUnit;
        } else {
            buffIconIndex = Math.ceil(buffedUnit / (0.25 * templates.UNITS[unit.name].strength))
        }
        const buffIcons = ['+', "▲", "★", "✸"];
        const buffIcon = buffIconIndex < buffIcons.length ? buffIcons[buffIconIndex - 1] : buffIcons[buffIcons.length - 1];    


        return (
            <svg 
                width={`${4*scale}`} 
                height={`${4*scale}`} 
                viewBox={`0 0 ${4*scale} ${6*scale}`}
                x={-2*scale} 
                y={-2*scale + (small ? 1 : 0)}
                opacity={unit.done_attacking ? 0.65 : 1.0}
            >

                <image href={civNameToShieldImgSrc(civName)} x={`${0.2*scale}`} y={`${0.8*scale}`} height={`${2*scale}`} width={`${2*scale}`}/>

                <g transform={`translate(${horizontalOffset}, ${verticalOffset})`}>
                    {spriteData[currentAnimation][currentFrame].map((row, y) => 
                        row.map((pixel, x) => {
                            if (Array.isArray(pixel) && pixel[3] === 0) return null;
                            
                            let color;
                            if (pixel === "team color 1") {
                                color = primaryColor;
                            } else if (pixel === "team color 2") {
                                color = secondaryColor;
                            } else {
                                color = `rgba(${pixel[0]}, ${pixel[1]}, ${pixel[2]}, ${pixel[3]/255})`;
                            }
    
                            return (
                                <rect
                                    key={`${x}-${y}`}
                                    x={Math.round(x * pixelSize * 100) / 100}
                                    y={Math.round(y * pixelSize * 100) / 100}
                                    width={Math.round(pixelSize * 100) / 100}
                                    height={Math.round(pixelSize * 100) / 100}
                                    fill={color}
                                />
                            );
                        })
                    )}
                </g>    
                
                {/* Health bar and stack size indicators remain at the bottom */}
                <rect x={`${scale}`} y={`${5.35*scale}`} width={`${2*scale}`} height={`${0.2*scale}`} fill="#ff0000" />
                <rect x={`${scale}`} y={`${5.35*scale}`} width={`${2*scale*healthPercentage}`} height={`${0.2*scale}`} fill="#00ff00" />
                
                {unit.stack_size > 1 && (
                    <>
                        <circle cx={`${2*scale + 0.8*scale}`} cy={`${4.5*scale}`} r={`${scale/2}`} fill="white" stroke="black" strokeWidth={0.1} />
                        <text x={`${2.8*scale}`} y={`${4.6*scale}`} style={{ fontSize: `${scale}px`, textAnchor: "middle", dominantBaseline: "middle" }}>{unit.stack_size}</text>
                    </>
                )}

            {buffedUnit > 0 && <circle opacity={unit.done_attacking ? 0.5 : 1.0} cx={`${1.2*scale}`} cy={`${4.5*scale}`} r={`${0.5 * scale}`} fill={primaryColor} stroke={secondaryColor} strokeWidth={0.15} />}
            {buffedUnit > 0 && <text opacity={unit.done_attacking ? 0.5 : 1.0} x={`${1.2*scale}`} y={`${4.5*scale}`} style={{ fontSize: `${scale * 0.5}px`, textAnchor: "middle", dominantBaseline: "middle", fill: unitCivTemplate?.darkmode ? "white" : "black" }}> {buffIcon} </text>}

            </svg>
        );
    }

    else {
        return <BasicUnit unit={unit} small={small} templates={templates} civsById={civsById} />
    }
};