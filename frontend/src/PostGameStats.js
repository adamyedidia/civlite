import React from 'react';
import './PostGameStats.css';

import Plot from 'react-plotly.js';
import { FormControl, InputLabel, Select, MenuItem, FormGroup, FormControlLabel, Switch } from '@mui/material';

const PostGameStats = ({ gameState, gameId, URL, templates }) => {
    const [civInfos, setCivInfos] = React.useState(null);
    const [stats, setStats] = React.useState(null);
    const [displayStat, setDisplayStat] = React.useState('total_yields');
    const [colorByCiv, setColorByCiv] = React.useState(true);
    const [showDeclines, setShowDeclines] = React.useState(true);
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
    const last_turn = gameState.turn_num - 1;
    const playerNumPlotColors = ['red', 'green', 'blue', 'orange', 'purple', 'black', 'pink', 'brown'];

    const plotData = Object.keys(civInfos).flatMap(civId => {
        const start_turn = civInfos[civId].start_turn;
        const decline_turn = civInfos[civId].decline_turn || last_turn;
        const end_turn = civInfos[civId].dead_turn || last_turn;
        const x = Array.from({ length: end_turn - start_turn + 1 }, (_, index) => index + start_turn);
        const y = activeData[civId].slice(0, end_turn - start_turn + 1);
    
        const line_color = colorByCiv ? templates.CIVS[gameState.civs_by_id[civId].name].primary_color : playerNumPlotColors[civInfos[civId].player_num];
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
                    gameState.civs_by_id[civId].name + ' (' + gameState.game_player_by_player_num[civInfos[civId].player_num].username + ')' :
                    gameState.game_player_by_player_num[civInfos[civId].player_num].username,
                x: solidX,
                y: solidY,
                marker: { size: 6, color: dot_color },
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
                marker: { size: 5, color: dot_color },
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
    const plotShapes = [];
    if (showDeclines) {
        Object.keys(civInfos).forEach(civId => {
            const startTurn = civInfos[civId].start_turn;
            if (startTurn > 1) {
                const color = colorByCiv ? templates.CIVS[gameState.civs_by_id[civId].name].primary_color : playerNumPlotColors[civInfos[civId].player_num];
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
                    legendgroup: `group${civId}`,
                    showlegend: false,
                });
            }
        });
    }

    return (
        <div className="post-game-stats">
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
    );
};

export default PostGameStats;

