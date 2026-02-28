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
            try {
                const { oscillator1, oscillator2 } = bgMusicRef.current;
                oscillator1.stop();
                oscillator2.stop();
            } catch (error) {
                console.log('Error stopping music:', error);
            }
            bgMusicRef.current = null;
        }
    }, []);

    const startBackgroundMusic = useCallback((type = 'battle') => {
        if (soundEnabledRef.current) {
            try {
                // Stop any existing background music first
                if (bgMusicRef.current) {
                    try {
                        bgMusicRef.current.oscillator1.stop();
                        bgMusicRef.current.oscillator2.stop();
                    } catch (e) { }
                    bgMusicRef.current = null;
                }

                const audioContext = getAudioContext();
                const oscillator1 = audioContext.createOscillator();
                const oscillator2 = audioContext.createOscillator();
                const gainNode = audioContext.createGain();

                oscillator1.type = 'sine';
                oscillator2.type = 'sine';

                if (type === 'battle') {
                    oscillator1.frequency.value = 130.81; // C3
                    oscillator2.frequency.value = 164.81; // E3
                } else {
                    oscillator1.frequency.value = 110; // A2
                    oscillator2.frequency.value = 146.83; // D3
                }

                gainNode.gain.value = 0.03; // Very subtle

                oscillator1.connect(gainNode);
                oscillator2.connect(gainNode);
                gainNode.connect(audioContext.destination);

                bgMusicRef.current = { oscillator1, oscillator2, audioContext };

                oscillator1.start();
                oscillator2.start();
            } catch (error) {
                console.log('Background music not available:', error);
            }
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
