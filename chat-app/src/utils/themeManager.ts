import themesConfig from '../themes.json';

export interface ThemeColors {
  primary: string;
  primaryHover: string;
  secondary: string;
  success: string;
  warning: string;
  danger: string;
  info: string;
  background: string;
  surface: string;
  surfaceHover: string;
  border: string;
  text: string;
  textSecondary: string;
  textMuted: string;
  shadow: string;
  shadowHover: string;
  chatBubbleUser: string;
  chatBubbleUserText: string;
  chatBubbleAssistant: string;
  chatBubbleAssistantText: string;
  inputBackground: string;
  inputBorder: string;
  inputFocus: string;
}

export interface Theme {
  name: string;
  icon: string;
  colors: ThemeColors | 'auto';
}

export type ThemeId = keyof typeof themesConfig.themes;

export class ThemeManager {
  private currentTheme: ThemeId = 'system';
  private mediaQuery: MediaQueryList;
  private listeners: Array<(theme: ThemeId, colors: ThemeColors) => void> = [];

  constructor() {
    this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    this.mediaQuery.addEventListener('change', this.handleSystemThemeChange.bind(this));
    this.loadSavedTheme();
  }

  private loadSavedTheme(): void {
    const saved = localStorage.getItem('chat-app-theme') as ThemeId;
    if (saved && this.isValidTheme(saved)) {
      this.currentTheme = saved;
    }
    this.applyTheme(this.currentTheme);
  }

  private isValidTheme(theme: string): theme is ThemeId {
    return theme in themesConfig.themes;
  }

  private handleSystemThemeChange(): void {
    if (this.currentTheme === 'system') {
      this.applyTheme('system');
    }
  }

  public setTheme(themeId: ThemeId): void {
    this.currentTheme = themeId;
    localStorage.setItem('chat-app-theme', themeId);
    this.applyTheme(themeId);
  }

  public getCurrentTheme(): ThemeId {
    return this.currentTheme;
  }

  public getAvailableThemes(): Array<{ id: ThemeId; theme: Theme }> {
    return Object.entries(themesConfig.themes).map(([id, theme]) => ({
      id: id as ThemeId,
      theme: theme as Theme
    }));
  }

  public getThemeColors(themeId: ThemeId): ThemeColors {
    const theme = themesConfig.themes[themeId] as Theme;
    
    if (theme.colors === 'auto') {
      // System theme - use light or dark based on system preference
      const systemTheme = this.mediaQuery.matches ? 'dark' : 'light';
      return themesConfig.themes[systemTheme].colors as ThemeColors;
    }
    
    return theme.colors as ThemeColors;
  }

  private applyTheme(themeId: ThemeId): void {
    const colors = this.getThemeColors(themeId);
    
    // Apply CSS custom properties
    const root = document.documentElement;
    Object.entries(colors).forEach(([key, value]) => {
      const cssVar = `--color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
      root.style.setProperty(cssVar, value);
    });

    // Add theme class to body for additional styling
    document.body.className = document.body.className.replace(/theme-\w+/g, '');
    document.body.classList.add(`theme-${themeId}`);

    // Notify listeners
    this.listeners.forEach(listener => listener(themeId, colors));
  }

  public onThemeChange(callback: (theme: ThemeId, colors: ThemeColors) => void): void {
    this.listeners.push(callback);
    // Immediately call with current theme
    callback(this.currentTheme, this.getThemeColors(this.currentTheme));
  }

  public removeThemeChangeListener(callback: (theme: ThemeId, colors: ThemeColors) => void): void {
    const index = this.listeners.indexOf(callback);
    if (index > -1) {
      this.listeners.splice(index, 1);
    }
  }
}