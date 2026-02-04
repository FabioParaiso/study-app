import '@testing-library/jest-dom';

const buildLocalStorageMock = () => {
    let store = {};
    return {
        getItem: (key) => (key in store ? store[key] : null),
        setItem: (key, value) => {
            store[key] = String(value);
        },
        removeItem: (key) => {
            delete store[key];
        },
        clear: () => {
            store = {};
        }
    };
};

if (!globalThis.localStorage || typeof globalThis.localStorage.clear !== 'function') {
    Object.defineProperty(globalThis, 'localStorage', {
        value: buildLocalStorageMock(),
        configurable: true
    });
}

if (typeof window !== 'undefined') {
    Object.defineProperty(window, 'alert', {
        value: () => {},
        configurable: true
    });
}

if (typeof process !== 'undefined' && process.stderr && !globalThis.__stderrFilterInstalled__) {
    const originalWrite = process.stderr.write.bind(process.stderr);
    process.stderr.write = (chunk, encoding, callback) => {
        const text = chunk instanceof Buffer ? chunk.toString() : String(chunk);
        if (text.includes('--localstorage-file')) {
            if (typeof callback === 'function') callback();
            return true;
        }
        return originalWrite(chunk, encoding, callback);
    };
    globalThis.__stderrFilterInstalled__ = true;
}
