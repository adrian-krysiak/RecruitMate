import { useEffect, useState } from 'react';

export function ThemeToggle() {
    const [isDarkMode, setIsDarkMode] = useState(() => {
        const savedMode = localStorage.getItem('theme');
        return savedMode === 'dark';
    });

    useEffect(() => {
        if (isDarkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    }, [isDarkMode]);

    const toggleTheme = () => {
        setIsDarkMode(prevMode => !prevMode);
    };

    return (
        <button
            id="themeToggleButton"
            onClick={toggleTheme}
        >
            {isDarkMode ? 'Light' : 'Dark'}
        </button>
    );
}