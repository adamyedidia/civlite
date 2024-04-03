import './ResetGamePage.css';

import { Button, TextField } from "@mui/material";

import { URL } from './settings';

const ResetGamePage = () => {
    const handleSubmit = () => {
        const gameID = document.getElementById('game-id').value;
        const turnNum = document.getElementById('turn-num').value;
        if (gameID === '' || turnNum === '') {
            return;
        }
        fetch(`${URL}/api/reset_game/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ game_id: gameID, turn_num: turnNum }),
        }).then(res => res.json()).then(data => {
            if (data.success) {
                alert("Game reset successfully!");
            } else {
                alert("Error resetting game!", data);
            }
        }).catch(err => {

            alert("Error resetting game!", err);
        });
    }





    return <div className="reset-game-page">
        <TextField id="game-id" label="Game ID" variant="standard" />
        <TextField id="turn-num" label="Turn Num" variant="standard" />

        <Button
            onClick={handleSubmit}
            variant="contained"
        >
            Reset Game

        </Button>
    </div>
}

export default ResetGamePage;