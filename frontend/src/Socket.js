import { URL } from './settings';
import io from 'socket.io-client';

let socket = io.connect(URL);

socket.on('connect', () => {
    console.log('connected');
});

socket.on('disconnect', () => {
    console.log('disconnected');
});

export default socket;