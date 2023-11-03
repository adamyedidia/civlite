import React, { Component } from 'react';

import { HexGrid, Layout, Hexagon, Text, Pattern, Path, Hex, GridGenerator } from 'react-hexgrid';
import './App.css';
import { Typography } from '@mui/material';
import { css } from '@emotion/react';

class App extends Component {

  render() {
    const hexagons = GridGenerator.parallelogram(-2, 3, -2, 1);

    return (
      <div
        className="basic-example "
        css={css`
          margin: 0;
          padding: 1em;
          font-family: sans-serif;
          background: #f0f0f0;
        `}
      >
        <h1>Basic example of HexGrid usage.</h1>
        <HexGrid width={1200} height={1000}>
          <Layout size={{ x: 7, y: 7 }}>
            {hexagons.map((hex, i) => (
              <Hexagon key={i} q={hex.q} r={hex.r} s={hex.s} onClick={() => console.log('hello')}>
                <Text x={-4} y={0} className="hex-text">{hex.q}</Text>
                <Text x={2} y={2}>{hex.r}</Text>
                <Text x={3} y={3}>{hex.s}</Text>
              </Hexagon>
            ))}
          </Layout>
        </HexGrid>
      </div>
    )

  }
}

export default App;
