import React from 'react';
import './PostGameStats.css';

import Plot from 'react-plotly.js';
import { FormControl, InputLabel, Select, MenuItem, FormGroup, FormControlLabel, Switch, Slider, Typography } from '@mui/material';
import PostGameLittleMovie from './PostGameLittleMovie';

const PostGameStats = ({ gameState, gameId, URL, templates }) => {
    const [civInfos, setCivInfos] = React.useState(null);
    const [stats, setStats] = React.useState(null);
    const [movieData, setMovieData] = React.useState(null);
    const [movieFrame, setMovieFrame] = React.useState(0);
    const [displayStat, setDisplayStat] = React.useState('total_yields');
    const [colorByCiv, setColorByCiv] = React.useState(true);
    const [showDeclines, setShowDeclines] = React.useState(true);
    const [smoothing, setSmoothing] = React.useState(0);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    React.useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`${URL}/api/postgame_stats/${gameId}`);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                const data = await response.json();
                setCivInfos(data.civ_infos);
                setStats(data.stats);
                setMovieData(data.movie_frames);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;

    const activeData = stats[displayStat];
    const last_turn = gameState.turn_num;
    const playerNumPlotColors = ['red', 'green', 'blue', 'orange', 'purple', 'black', 'pink', 'brown'];


    const getColor = (civId) => {
        if (colorByCiv) {
            return templates.CIVS[gameState.civs_by_id[civId].name].primary_color;
        } else {
            const playerNum = civInfos[civId].player_num;
            if (playerNum === null) {
                return 'grey';
            }
            return playerNumPlotColors[playerNum];
        }
    }

    const plotData = Object.keys(civInfos).flatMap(civId => {
        if (!activeData[civId]) {
            return [];
        }
        const start_turn = civInfos[civId].start_turn;
        const decline_turn = civInfos[civId].decline_turn || last_turn;
        const dead_turn = civInfos[civId].dead_turn || last_turn;
        const end_turn = (displayStat == 'score_per_turn' || displayStat == 'cumulative_score') ? decline_turn : dead_turn;
        const x = Array.from({ length: end_turn - start_turn + 1 }, (_, index) => index + start_turn);
        const rawy = activeData[civId].slice(0, end_turn - start_turn + 1);
        if (x.length !== rawy.length) {
            console.error("Data mismatch: 'x' and 'y' arrays must be the same length.");
            console.log(x.length, x)
            console.log(rawy.length, rawy)
            console.log(start_turn, decline_turn, end_turn, activeData[civId].length)
        }
        const smoothingFactor = smoothing / 100;
        const y = rawy.map((current, index, arr) => {
            let smoothedValue = 0;
            let normalizationFactor = 0;
            let weight = 1;
            for (let i = index; i >= 0; i--) {
                smoothedValue += weight * arr[i];
                normalizationFactor += weight;
                weight *= smoothingFactor;
            }
            return smoothedValue / normalizationFactor;
        });
    
        const line_color = getColor(civId);
        const dot_color = colorByCiv ? templates.CIVS[gameState.civs_by_id[civId].name].secondary_color : playerNumPlotColors[civInfos[civId].player_num];
    
        // Split the data into two parts: before and after the decline
        const solidX = x.filter(value => value <= decline_turn);
        const solidY = y.slice(0, solidX.length);
        const dotX = x.filter(value => value >= decline_turn);
        const dotY = y.slice(solidX.length - 1);
    
        const traces = [];
    
        const isFirstCivForPlayer = Object.keys(civInfos).findIndex(id => civInfos[id].player_num === civInfos[civId].player_num) === Object.keys(civInfos).indexOf(civId);
        const showLegend = colorByCiv || isFirstCivForPlayer;
        // Solid line trace
        if (solidX.length > 0) {
            traces.push({
                type: 'scatter',
                mode: 'lines+markers',
                name: colorByCiv ? 
                    gameState.civs_by_id[civId].name + ' (' + (gameState.game_player_by_player_num[civInfos[civId].player_num]?.username || 'Rebels') + ')' :
                    gameState.game_player_by_player_num[civInfos[civId].player_num]?.username || 'Rebels',
                x: solidX,
                y: solidY,
                marker: { size: 5, color: dot_color },
                line: {
                    color: line_color,
                    shape: 'linear',
                    dash: 'solid'
                },
                legendgroup: colorByCiv ? `group${civId}` : `group${civInfos[civId].player_num}`,
                showlegend: showLegend,
            });
        }
    
        // Dotted line trace
        if (dotX.length > 0) {
            traces.push({
                type: 'scatter',
                mode: 'lines+markers',
                x: dotX,
                y: dotY,
                marker: { size: 3, color: dot_color },
                line: {
                    color: line_color,
                    shape: 'linear',
                    dash: 'dot'
                },
                legendgroup: colorByCiv ? `group${civId}` : `group${civInfos[civId].player_num}`,
                showlegend: false,
            });
        }
    
        return traces;
    });
    const frameTurnNum = movieData[movieFrame].turn_num;
    const plotShapes = [
        {
            type: 'line',
            x0: frameTurnNum,
            x1: frameTurnNum,
            y0: 0,
            y1: 1,
            yref: 'paper', // This makes the line span the entire y-axis height
            line: {
                color: 'black',
                width: 2,
            },
        }
    ];
    if (showDeclines) {
        Object.keys(civInfos).forEach(civId => {
            const startTurn = civInfos[civId].start_turn;
            if (startTurn > 1 && civInfos[civId].player_num !== null) {
                const color = getColor(civId);
                plotShapes.push({
                    type: 'line',
                    x0: startTurn,
                    x1: startTurn,
                    y0: 0,
                    y1: 1,
                    yref: 'paper', // This makes the line span the entire y-axis height
                    line: {
                        color: color,
                        width: 2,
                        dash: 'dash'
                    },
                });
            }
        });
    }

    return (
        <div className="post-game-stats">
            <div className="post-game-graph">
            <div className="stat-selector-container">
                <FormControl fullWidth>
                    <InputLabel id="stat-select-label">Statistic</InputLabel>
                    <Select
                        labelId="stat-select-label"
                        id="stat-select"
                        value={displayStat}
                        label="Statistic"
                        onChange={(e) => setDisplayStat(e.target.value)}
                    >
                    {Object.keys(stats).map((statKey) => (
                        <MenuItem key={statKey} value={statKey}>
                            {statKey}
                        </MenuItem>
                    ))}
                    </Select>
                </FormControl>
                <FormControl fullWidth>
                    <InputLabel id="stat-select-label">Color by</InputLabel>
                    <Select
                        labelId="color-select-label"
                        id="color-select"
                        value={colorByCiv}
                        label="Color by"
                        onChange={(e) => setColorByCiv(e.target.value)}
                    >
                        <MenuItem value={false}>Player</MenuItem>
                        <MenuItem value={true}>Civ</MenuItem>
                    </Select>
                </FormControl>
                <FormControl fullWidth>
                    <FormGroup>
                        <FormControlLabel
                            control={
                                <Switch
                                    checked={showDeclines}
                                    onChange={(e) => setShowDeclines(e.target.checked)}
                                    name="showDeclinesToggle"
                                    color="primary"
                                />
                            }
                            label="Show Declines"
                        />
                    </FormGroup>
                </FormControl>
                <FormControl fullWidth>
                    <Typography id="smoothing-slider-label">
                        Smoothing: {smoothing}%
                    </Typography>
                    <Slider
                        aria-labelledby="smoothing-slider-label"
                        value={smoothing}
                        onChange={(e, newValue) => setSmoothing(newValue)}
                        valueLabelDisplay="auto"
                        step={1}
                        marks
                        min={0}
                        max={100}
                    />
                </FormControl>
            </div>
            <Plot
            data={plotData}
            layout={{
                xaxis: {
                    title: 'Turn',
                    rangemode: 'tozero'
                },
                yaxis: {
                    title: displayStat,
                    rangemode: 'tozero'
                },
                shapes: plotShapes,
                width: 850,
                height: 600,
            }}
            />
        </div>
        <div className="little-movie-container">
            <PostGameLittleMovie movieData={movieData} movieFrame={movieFrame} setMovieFrame={setMovieFrame} 
                getColor={getColor} civInfos={civInfos} finalGameState={gameState} />
        </div>
        </div>
    );
};

export default PostGameStats;

