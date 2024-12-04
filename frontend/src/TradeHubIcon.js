import tradeHubImg from './images/tradehub.png';
import scienceImg from './images/science.png';
import foodImg from './images/food.png';
import metalImg from './images/metal.png';
import woodImg from './images/wood.png';

const TradeHubIcon = ({ myGamePlayer, style, className }) => {
    const a7Tenet = myGamePlayer.a7_tenet_yield;
    if (!a7Tenet) return <img src={tradeHubImg} alt="Trade Hub" style={style} className={className} />;
    const overlay = a7Tenet === 'science' ? scienceImg : a7Tenet === 'food' ? foodImg : a7Tenet === 'metal' ? metalImg : a7Tenet === 'wood' ? woodImg : tradeHubImg;
    return (
        <div style={{ position: 'relative', width: 'fit-content', ...style }}  className={className}>
            <img src={tradeHubImg} alt="Trade Hub" style={{width: '100%'}}/>
            <img 
                src={overlay} 
                alt="Overlay" 
                style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '50%',
                    height: '50%'
                }}
            />
        </div>
    );

}

export default TradeHubIcon;