import { useRef, useEffect } from 'react';

export const ShrinkFontText = ({className, startFontSize, text, allowWrap}) => {
    startFontSize = startFontSize || 16;
    allowWrap = allowWrap || false;
    const nameRef = useRef(null);

    useEffect(() => {
        if (!nameRef.current) return;
        const element = nameRef.current;
        let fontSize = startFontSize;

        element.style.fontSize = `${fontSize}px`;
        element.style.whiteSpace = allowWrap ? "normal" : "nowrap";

        // Adjust font size until the text fits or reaches the minimum font size
        while (element.parentNode.scrollWidth > element.parentNode.clientWidth && fontSize > 4) {
            fontSize--; // Decrease the font size
            element.style.fontSize = `${fontSize}px`; // Apply the new font size
        }
    }, [text]);

    return <div className={className} ref={nameRef}>
        {text}
        </div>;
}