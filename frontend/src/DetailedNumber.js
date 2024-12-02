import React from "react";
import "./DetailedNumber.css";

const displayValue = (value) => {
    // If it's an integer, don't show the decimal places, otherwise show 2 decimal places
    return value % 1 === 0 ? value >= 100 ? value : value.toFixed(0) : value >= 10 ? value.toFixed(1) : value.toFixed(2);
}

export const DetailedNumberTooltipContent = ({ detailedNumber, titleHeader }) => {
    const liFormatedData = Object.entries(detailedNumber.data).map(([key, value]) => 
        <li key={key}>
            <div className="detailed-number-tooltip-value">{displayValue(value)}</div>
            <div className="detailed-number-tooltip-key">{key}</div>
        </li>
    );
    return <div className="detailed-number-tooltip">
        {titleHeader && <h3>{titleHeader}</h3>}
        <ul>{liFormatedData}</ul>
    </div>
}
