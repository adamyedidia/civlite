import { CIV_TO_FLAG_NAME } from './CivToFlagName.js';


export function civNameToShieldImgSrc(civName) {
    const flagName = CIV_TO_FLAG_NAME[civName];
    return `/flags/${flagName}-shield-large.png`;
}

export function civNameToFlagImgSrc(civName) {
    const flagName = CIV_TO_FLAG_NAME[civName];
    return `/flags/${flagName}-large.png`;
}