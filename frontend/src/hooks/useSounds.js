import { useEffect, useRef, useState, useCallback } from 'react';

// Shared AudioContext to avoid creating multiple instances
let sharedAudioContext = null;

const getAudioContext = () => {
    if (!sharedAudioContext || sharedAudioContext.state === 'closed') {
        sharedAudioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    // Resume if suspended (browser autoplay policy)
    if (sharedAudioContext.state === 'suspended') {
        sharedAudioContext.resume();
    }
    return sharedAudioContext;
};

// Create tone using shared AudioContext
const createTone = (frequency, duration, type = 'sine') => {
    try {
        const audioContext = getAudioContext();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = frequency;
        oscillator.type = type;

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + duration);
    } catch (error) {
        console.log('Audio not available:', error);
    }
};

export const useSounds = () => {
    const [isMuted, setIsMuted] = useState(() => {
        const saved = localStorage.getItem('soundsMuted');
        return saved === 'true';
    });

    const bgMusicRef = useRef(null);
    const soundEnabledRef = useRef(!isMuted);

    useEffect(() => {
        soundEnabledRef.current = !isMuted;
        localStorage.setItem('soundsMuted', isMuted.toString());

        if (isMuted && bgMusicRef.current) {
            stopBackgroundMusic();
        }
    }, [isMuted]);

    // Initialize audio context on first user interaction
    const initAudio = useCallback(() => {
        getAudioContext();
    }, []);

    const playCorrectSound = useCallback(() => {
        if (soundEnabledRef.current) {
            // Happy ascending notes
            createTone(523.25, 0.15); // C5
            setTimeout(() => createTone(659.25, 0.15), 100); // E5
            setTimeout(() => createTone(783.99, 0.2), 200); // G5
        }
    }, []);

    const playWrongSound = useCallback(() => {
        if (soundEnabledRef.current) {
            // Descending sad notes
            createTone(349.23, 0.2, 'sawtooth'); // F4
            setTimeout(() => createTone(293.66, 0.3, 'sawtooth'), 150); // D4
        }
    }, []);

    const playClickSound = useCallback(() => {
        if (soundEnabledRef.current) {
            createTone(800, 0.05, 'square');
        }
    }, []);

    const playTimerWarning = useCallback(() => {
        if (soundEnabledRef.current) {
            createTone(880, 0.1, 'triangle');
        }
    }, []);

    const playBattleStart = useCallback(() => {
        if (soundEnabledRef.current) {
            createTone(440, 0.15);
            setTimeout(() => createTone(554.37, 0.15), 150);
            setTimeout(() => createTone(659.25, 0.2), 300);
        }
    }, []);

    const playCompleteSound = useCallback(() => {
        if (soundEnabledRef.current) {
            // Victory fanfare
            createTone(523.25, 0.15);
            setTimeout(() => createTone(659.25, 0.15), 150);
            setTimeout(() => createTone(783.99, 0.15), 300);
            setTimeout(() => createTone(1046.50, 0.3), 450);
        }
    }, []);

    const stopBackgroundMusic = useCallback(() => {
        if (bgMusicRef.current) {
            try { bgMusicRef.current.stop(); } catch (e) {}
            bgMusicRef.current = null;
        }
    }, []);

    const startBackgroundMusic = useCallback((type = 'battle') => {
        if (!soundEnabledRef.current) return;
        if (bgMusicRef.current) {
            try { bgMusicRef.current.stop(); } catch (e) {}
            bgMusicRef.current = null;
        }
        try {
            const audioContext = getAudioContext();
            let stopped = false;

            const tracks = {
                // Calm pentatonic loop for practice
                practice: {
                    melody: [392.00, 440.00, 493.88, 440.00, 392.00, 349.23, 392.00, 329.63],
                    bass:   [130.81, 146.83, 130.81, 110.00],
                    tempo: 0.45,
                    melodyGain: 0.05,
                    bassGain: 0.04,
                    melodyWave: 'sine',
                    bassWave: 'triangle',
                },
                // Epic boss battle music replacing default battle music
                battle: {
                    melody: [293.66, 311.13, 349.23, 311.13, 293.66, 261.63, 246.94, 261.63], // D4, D#4, F4, D#4, D4, C4, B3, C4
                    bass:   [146.83, 130.81, 123.47, 110.00], // D3, C3, B2, A2
                    tempo: 0.18,
                    melodyGain: 0.07,
                    bassGain: 0.06,
                    melodyWave: 'sawtooth',
                    bassWave: 'sawtooth',
                },
            };

            const t = tracks[type] || tracks.battle;
            const loopLen = t.melody.length * t.tempo;

            const scheduleNote = (freq, start, dur, gain, wave) => {
                const osc = audioContext.createOscillator();
                const g = audioContext.createGain();
                osc.type = wave;
                osc.frequency.value = freq;
                osc.connect(g);
                g.connect(audioContext.destination);
                g.gain.setValueAtTime(gain, start);
                g.gain.exponentialRampToValueAtTime(0.001, start + dur * 0.85);
                osc.start(start);
                osc.stop(start + dur);
            };

            const scheduleLoop = (startTime) => {
                if (stopped) return;
                t.melody.forEach((freq, i) =>
                    scheduleNote(freq, startTime + i * t.tempo, t.tempo * 0.8, t.melodyGain, t.melodyWave)
                );
                const bassStep = loopLen / t.bass.length;
                t.bass.forEach((freq, i) =>
                    scheduleNote(freq, startTime + i * bassStep, bassStep * 0.7, t.bassGain, t.bassWave)
                );
                setTimeout(() => scheduleLoop(startTime + loopLen), (loopLen - 0.3) * 1000);
            };

            scheduleLoop(audioContext.currentTime + 0.1);
            bgMusicRef.current = { stop: () => { stopped = true; } };
        } catch (error) {
            console.log('Background music not available:', error);
        }
    }, []);

    const toggleMute = useCallback(() => {
        // Initialize audio on user interaction (required by browsers)
        getAudioContext();
        setIsMuted(prev => !prev);
    }, []);

    return {
        isMuted,
        toggleMute,
        initAudio,
        playCorrectSound,
        playWrongSound,
        playClickSound,
        playTimerWarning,
        playBattleStart,
        playCompleteSound,
        startBackgroundMusic,
        stopBackgroundMusic
    };
};
