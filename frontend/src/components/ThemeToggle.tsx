import { useEffect, useState, useCallback } from 'react';
import { STORAGE_KEYS, THEME } from '../constants';
import { StorageService } from '../utils/storage';

export function ThemeToggle() {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const savedMode = StorageService.getString(STORAGE_KEYS.THEME);
        return savedMode === THEME.DARK;
    });

    useEffect(() => {
        const theme = isDarkMode ? THEME.DARK : THEME.LIGHT;
        document.documentElement.setAttribute('data-theme', theme);
        StorageService.setString(STORAGE_KEYS.THEME, theme);
    }, [isDarkMode]);

    const toggleTheme = useCallback(() => {
        setIsDarkMode(prevMode => !prevMode);
    }, []);

    return (
        <button
            id="themeToggleButton"
            onClick={toggleTheme}
            aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
            type="button"
        >
            {isDarkMode ? '☀️ Light' : '🌙 Dark'}
        </button>
    );
}