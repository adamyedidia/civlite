const EngineStates = {
    ANIMATING: 'animating',  // Playing the movie
    ROLLING: 'rolling',  // Waiting for the server to send update signal
    PLAYING: 'playing',  // Taking player actions
    GAME_OVER: 'game_over',  // Post game screen
};

export default EngineStates;

