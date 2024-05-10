import React from 'react';
import { HexGrid, Layout, Hexagon } from 'react-hexgrid';

const PostGameLittleMovie = ({ movieData, movieFrame, setMovieFrame, getColor, civInfos }) => {
    const thisFrame = movieData[movieFrame];
    const [paused, setPaused] = React.useState(false);
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
    console.log(civInfos)
    return <div className='little-movie'>
    <HexGrid width={400} height={400}>
        <Layout size={{ x: 3, y: 3 }}>
            {thisFrame.hexes.map(hex => {
                return <Hexagon key={`${hex.coords.q}-${hex.coords.r}-${hex.coords.s}`} q={hex.coords.q} r={hex.coords.r} s={hex.coords.s} 
                    style={{
                        fill: hex.civ ? getColor(hex.civ, thisFrame.turn_num) : 'grey',
                        opacity: (hex.civ && civInfos[hex.civ].decline_turn && civInfos[hex.civ].decline_turn < thisFrame.turn_num) ? 0.5 : 1.0
                    }}
                >
                    {hex.city && <rect x={-1} y={-0.5} width={2} height={1} fill='black' />  }
                    {hex.camp && <polygon points="-1,0.5 1,0.5 0,-1" fill='red' />}
                </Hexagon>
            })}
        </Layout>
    </HexGrid>;
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

