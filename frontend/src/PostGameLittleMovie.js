import React from 'react';
import { HexGrid, Layout, Hexagon } from 'react-hexgrid';

const PostGameLittleMovie = ({ movieData, movieFrame, setMovieFrame, getColor, civInfos, finalGameState }) => {
    const thisFrame = movieData[movieFrame];
    const [paused, setPaused] = React.useState(true);
    const [tickInterval, setTickInterval] = React.useState(null);

    React.useEffect(() => {
        if (paused) {
            clearInterval(tickInterval);
        } else {
            const interval = setInterval(() => {
                setMovieFrame(prevFrame => (prevFrame + 1) % movieData.length);
            }, 250);
            setTickInterval(interval);
            return () => clearInterval(interval);
        }
    }, [paused, setMovieFrame, movieData.length]);

    const handleScrubberChange = (event) => {
        const newFrame = parseInt(event.target.value, 10);
        setMovieFrame(newFrame);
    };
    return <div className='little-movie'>
    <HexGrid width={400} height={400}>
        <Layout size={{ x: 3, y: 3 }}>
            {thisFrame.hexes.map(hex => {
                const city_w = hex.puppet ? 2 : 2.5
                const city_h = hex.puppet ? 1.25 : 1.75
                const civ = finalGameState.civs_by_id[hex.civ]
                let civName;
                if (civ) {
                    const civPlayerNum = civInfos[hex.civ].player_num
                    civName = civPlayerNum ? `${civ.name} (${finalGameState.game_player_by_player_num[civPlayerNum].username})` : civ.name;
                }
                return <Hexagon key={`${hex.coords.q}-${hex.coords.r}-${hex.coords.s}`} q={hex.coords.q} r={hex.coords.r} s={hex.coords.s} 
                    style={{
                        fill: hex.civ ? getColor(hex.civ, thisFrame.turn_num) : 'grey',
                        fillOpacity: (hex.civ && civInfos[hex.civ].decline_turn && civInfos[hex.civ].decline_turn < thisFrame.turn_num) ? 0.5 : 1.0
                    }}
                >
                    {civName && <title>{civName}</title>}
                    {hex.city && <rect x={-city_w * 0.5} y={-city_h * 0.5} width={city_w} height={city_h} fill='black' fillOpacity={1} {...(hex.puppet ? {rx: "1", ry: "1"} : {})}/>  }
                    {hex.camp && <polygon points="-1,0.5 1,0.5 0,-1" fill='red' />}
                </Hexagon>
            })}
        </Layout>
    </HexGrid>
    <div>Turn {thisFrame.turn_num}</div>
    <input
        type="range"
        min="0"
        max={movieData.length - 1}
        value={movieFrame}
        onChange={handleScrubberChange}
        style={{ width: '100%', marginTop: '10px' }}
    />
    <button onClick={() => setPaused(!paused)}>
        {paused ? '▶️' : '⏸️'}
    </button>
    </div>
};

export default PostGameLittleMovie;

