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

export const CityDetailPanel = ({ title, icon, hideStored, noFocus, selectedCity, 
    override_stored_amount, override_income, override_income_base, override_income_focus, 
    total_prefix, total_tooltip, handleClickFocus, children }) => {

    const storedAmount = override_stored_amount !== undefined ? override_stored_amount : selectedCity[title];
    const projected_income_total = override_income !== undefined ? override_income : selectedCity[`projected_income`][title];
    const projected_income_base = override_income_base !== undefined ? override_income_base : selectedCity['projected_income_base'][title];
    const projected_income_focus = (override_income_focus !== undefined || noFocus) ? override_income_focus : selectedCity['projected_income_focus'][title];
    const projected_total = storedAmount + projected_income_total;
    const projected_total_rounded = Math.floor(projected_total);
    const projected_total_display = `${total_prefix ? total_prefix : ""}${projected_total_rounded}`;

    const projected_total_rounded_2 = Math.floor(projected_total * 100) / 100;
    const totalAmountTooltip = `${projected_total_rounded_2} ${title} ${total_tooltip}`;

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
                    <TextOnIcon image={hexesImg} tooltip={`${projected_income_base.toFixed(2)} ${title} produced this turn.`}> {roundValue(projected_income_base)} </TextOnIcon>
                    {!noFocus && (
                        <>
                            +
                            <FocusSelectionOption focus={title} isSelected={selectedCity?.focus === title} amount={projected_income_focus} onClick={() => handleClickFocus(title)} />
                        </>
                    )}
                </div>
            </div>
            <div className="panel-content">
                {children}
            </div>
        </div>
    );
};


