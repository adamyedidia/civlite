import React from 'react';
import crateImg from './images/crate.png';
import hexesImg from './images/hexes.png';
import workerImg from "./images/worker.png";

import { TextOnIcon } from './TextOnIcon';

const roundValue = (value) => {
    return value < 10 ? value.toFixed(1) : Math.round(value);
};

const FocusSelectionOption = ({ focus, amount, onClick, isSelected }) => {
    return (
        <div
            className={`focus-selection-option ${focus} ${isSelected ? 'selected' : ''}`}
            onClick={onClick}
        >
            <TextOnIcon image={workerImg} tooltip={isSelected ? `+${amount.toFixed(2)} ${focus} from city focus` : "Click to focus"}>
                {amount.toFixed(1)}
            </TextOnIcon>
        </div>
    );
};

export const CityDetailPanel = ({ title, icon, hideStored, selectedCity, handleClickFocus, children }) => {

    const storedAmount = selectedCity[title];
    const projected_income_total = selectedCity[`projected_income`][title];
    const projected_income_base = selectedCity['projected_income_base'][title];
    const projected_income_focus = selectedCity['projected_income_focus'][title];
    const projected_total = title == 'science' ? projected_income_total : storedAmount + projected_income_total;
    const projected_total_rounded = Math.floor(projected_total);
    let projected_total_display;
    switch (title) {
        case 'science':
            projected_total_display = `+${projected_total_rounded}`;
            break;
        // If we need custom display for any others, can add it here.
        default:
            projected_total_display = projected_total_rounded.toString();
            break;
    }
    const projected_total_rounded_2 = Math.floor(projected_total * 100) / 100;
    let totalAmountTooltip;
    switch (title) {
        case 'science':
            totalAmountTooltip = `${projected_total_rounded_2} ${title} produced by this city.`;
            break;
        case 'food':
            totalAmountTooltip = `${projected_total_rounded_2} ${title} after this turn.`;
            break;
        default:
            totalAmountTooltip = `${projected_total_rounded_2} ${title} available to spend this turn.`;
    }

    const storedStyle = hideStored ? { visibility: 'hidden' } : {};

    return (
        <div className={`city-detail-panel ${title}-area`}>
            <div className="panel-header">
                <div className="panel-icon">
                    <img src={icon} />
                </div>
                <div className="amount-total">
                    <TextOnIcon tooltip={totalAmountTooltip}>{projected_total_display}</TextOnIcon>
                </div>

                <div className="panel-banner">
                    =
                    <TextOnIcon image={crateImg} style={storedStyle} tooltip={hideStored ? null : `${storedAmount.toFixed(2)} ${title} stored from last turn.`}> {roundValue(storedAmount)} </TextOnIcon>
                    <div>+</div>
                    <TextOnIcon image={hexesImg} tooltip={`${projected_income_base.toFixed(2)} ${title} produced this turn without focus.`}> {roundValue(projected_income_base)} </TextOnIcon>
                    +
                    <FocusSelectionOption focus={title} isSelected={selectedCity?.focus === title} amount={projected_income_focus} onClick={() => handleClickFocus(title)} />
                </div>
            </div>
            <div className="panel-content">
                {children}
            </div>
        </div>
    );
};


