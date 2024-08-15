import React from 'react';
import "./CityDetailPanel.css";
import crateImg from './images/crate.png';
import hexesImg from './images/hexes.png';
import workerImg from "./images/worker.png";

import { WithTooltip } from './WithTooltip';
import { TextOnIcon } from './TextOnIcon';

const toFixedRndDown = (value, digits) => {
    const result = Math.floor(value * Math.pow(10, digits)) / Math.pow(10, digits);
    return result.toFixed(digits);
}

const roundValue = (value) => {
    return value < 10 ? toFixedRndDown(value, 1) : Math.floor(value);
};

const FocusSelectionOption = ({ focus, amount, onClick, onDoubleClick, hasPuppets, isSelected }) => {
    let clickTimeout = null;
    const handleClick = () => {
        if (clickTimeout !== null) {
            clearTimeout(clickTimeout);
            clickTimeout = null;
            onDoubleClick();
        } else {
            clickTimeout = setTimeout(() => {
                onClick();
                clearTimeout(clickTimeout);
                clickTimeout = null;
            }, 300); // 300 ms delay to distinguish between single and double click
        }
    };
    const tooltip = <>
        {isSelected ? <p>{`+${toFixedRndDown(amount, 2)} ${focus} from focus`}</p> : <p>Click to focus</p>}
        {hasPuppets && <p>dbl click = include puppets</p>}
    </>

    return (
        <div
            className={`focus-selection-option ${focus} ${isSelected ? 'selected' : ''}`}
            onClick={hasPuppets ? handleClick : onClick}
        >
            <TextOnIcon image={workerImg} tooltip={tooltip}>
                {toFixedRndDown(amount, 1)}
            </TextOnIcon>
        </div>
    );
};

const PuppetIncomeTooltip = ({projectedIncomePuppets, projectedIncomePuppetsTotal, title}) => {
    return (<>
        <b>{toFixedRndDown(projectedIncomePuppetsTotal, 2)} {title} from puppets:</b>
        <table><tbody>
            {Object.entries(projectedIncomePuppets).map(([puppetId, incomeAndDistance]) => <tr key={puppetId}><td>+{toFixedRndDown(incomeAndDistance[0], 2)}</td><td>{puppetId}</td></tr>)}
        </tbody></table>
    </>);
}

export const CityDetailPanel = ({ title, icon, hideStored, noFocus, selectedCity, 
   total_tooltip, handleClickFocus, children }) => {

    const storedAmount = selectedCity[title];
    const projected_income_total = selectedCity[`projected_income`][title];
    const projected_income_base = selectedCity['projected_income_base'][title];
    const projected_income_focus = selectedCity['projected_income_focus'][title];
    const projected_total = (hideStored ? 0 : storedAmount) + (noFocus ? projected_income_base : projected_income_total);
    const projected_total_rounded = Math.floor(projected_total);
    const projected_total_display = `${hideStored ? "+" : ""}${projected_total_rounded}`;

    const projected_total_rounded_2 = Math.floor(projected_total * 100) / 100;
    const totalAmountTooltip = `${projected_total_rounded_2} ${title} ${total_tooltip}`;

    const storedStyle = hideStored ? { visibility: 'hidden' } : {};
    const projectedIncomePuppets = selectedCity?.projected_income_puppets?.[title];
    const hasPuppetsEvenIfNoIncome = Object.keys(selectedCity?.projected_income_puppets?.["wood"] || {}).length > 0;
    const hasPuppets = projectedIncomePuppets && Object.keys(projectedIncomePuppets).length > 0;
    const projectedIncomePuppetsTotal = hasPuppets ? Object.values(projectedIncomePuppets).reduce((total, puppetIncomeAndDistance) => total + puppetIncomeAndDistance[0], 0) : null;
    const projectedIncomePuppetsTooltip = hasPuppets ? <PuppetIncomeTooltip title={title} projectedIncomePuppets={projectedIncomePuppets} projectedIncomePuppetsTotal={projectedIncomePuppetsTotal} /> : null;
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
                    <TextOnIcon image={crateImg} style={storedStyle} tooltip={hideStored ? null : `${toFixedRndDown(storedAmount, 2)} ${title} stored from last turn.`}> {roundValue(storedAmount)} </TextOnIcon>
                    <div>+</div>
                    <TextOnIcon image={hexesImg} tooltip={`${toFixedRndDown(projected_income_base, 2)} ${title} produced this turn.`}> {roundValue(projected_income_base)} </TextOnIcon>
                    {!noFocus && (
                        <>
                            +
                            <FocusSelectionOption focus={title} isSelected={selectedCity?.focus === title} amount={projected_income_focus} 
                                hasPuppets={hasPuppetsEvenIfNoIncome}
                                onClick={() => handleClickFocus(title)} onDoubleClick={() => handleClickFocus(title, true)} />
                        </>
                    )}
                </div>
            </div>
            <div className={children || hasPuppets ? "panel-content" : ""}>
                {hasPuppets && (<div className="puppet-income-container panel-banner">
                    <div>+</div>
                    <WithTooltip tooltip={projectedIncomePuppetsTooltip} alignBottom={true}> 
                        <div className="puppet-income">
                            {roundValue(projectedIncomePuppetsTotal)} 
                        </div>
                    </WithTooltip>
                </div>)}
                {children}
            </div>
        </div>
    );
};


