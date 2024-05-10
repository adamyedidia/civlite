const EngineStates = {
    ANIMATING: 'animating',  // Playing the movie
    ROLLING: 'rolling',  // Waiting for the server to send update signal
    PLAYING: 'playing',  // Taking player actions
    GAME_OVER: 'game_over',  // 
    FINAL_MOVIE: 'final_movie',  // Playing the final movie
};

export default EngineStates;

