export const playSound = (type) => {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();

    if (type === 'success') {
        // "Ching!" sound - high pitch coin sound
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.type = 'sine';
        oscillator.frequency.setValueAtTime(1200, audioContext.currentTime);
        oscillator.frequency.exponentialRampToValueAtTime(2000, audioContext.currentTime + 0.1);

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.3);
    } else if (type === 'error') {
        // "Buzz" sound - low pitch warning
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.type = 'sawtooth';
        oscillator.frequency.setValueAtTime(150, audioContext.currentTime);
        oscillator.frequency.linearRampToValueAtTime(100, audioContext.currentTime + 0.3);

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.linearRampToValueAtTime(0.01, audioContext.currentTime + 0.3);

        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.3);
    }
};
