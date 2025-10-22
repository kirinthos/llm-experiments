import { ref, computed, onMounted, onUnmounted, readonly } from 'vue'
import themesConfig from '../themes.json'

export interface ThemeColors {
  primary: string
  primaryHover: string
  secondary: string
  success: string
  warning: string
  danger: string
  info: string
  background: string
  surface: string
  surfaceHover: string
  border: string
  text: string
  textSecondary: string
  textMuted: string
  shadow: string
  shadowHover: string
  chatBubbleUser: string
  chatBubbleUserText: string
  chatBubbleAssistant: string
  chatBubbleAssistantText: string
  inputBackground: string
  inputBorder: string
  inputFocus: string
}

export interface Theme {
  name: string
  icon: string
  colors: ThemeColors | 'auto'
}

export type ThemeId = keyof typeof themesConfig.themes

export function useTheme() {
  const currentTheme = ref<ThemeId>('system')
  const mediaQuery = ref<MediaQueryList>()

  // Get available themes
  const availableThemes = computed(() => {
    return Object.entries(themesConfig.themes).map(([id, theme]) => ({
      id: id as ThemeId,
      theme: theme as Theme
    }))
  })

  // Get current theme colors
  const currentColors = computed(() => {
    return getThemeColors(currentTheme.value)
  })

  // Get current theme info
  const currentThemeInfo = computed(() => {
    const themes = availableThemes.value
    return themes.find(t => t.id === currentTheme.value)
  })

  function getThemeColors(themeId: ThemeId): ThemeColors {
    const theme = themesConfig.themes[themeId] as Theme
    
    if (theme.colors === 'auto') {
      // System theme - use light or dark based on system preference
      const systemTheme = mediaQuery.value?.matches ? 'dark' : 'light'
      return themesConfig.themes[systemTheme].colors as ThemeColors
    }
    
    return theme.colors as ThemeColors
  }

  function applyTheme(themeId: ThemeId) {
    const colors = getThemeColors(themeId)
    
    // Apply CSS custom properties
    const root = document.documentElement
    Object.entries(colors).forEach(([key, value]) => {
      const cssVar = `--color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`
      root.style.setProperty(cssVar, value)
    })

    // Add theme class to body for additional styling
    document.body.className = document.body.className.replace(/theme-\w+/g, '')
    document.body.classList.add(`theme-${themeId}`)
  }

  function setTheme(themeId: ThemeId) {
    currentTheme.value = themeId
    localStorage.setItem('chat-app-theme', themeId)
    applyTheme(themeId)
  }

  function handleSystemThemeChange() {
    if (currentTheme.value === 'system') {
      applyTheme('system')
    }
  }

  function loadSavedTheme() {
    const saved = localStorage.getItem('chat-app-theme') as ThemeId
    if (saved && saved in themesConfig.themes) {
      currentTheme.value = saved
    }
    applyTheme(currentTheme.value)
  }

  onMounted(() => {
    // Set up media query for system theme detection
    mediaQuery.value = window.matchMedia('(prefers-color-scheme: dark)')
    mediaQuery.value.addEventListener('change', handleSystemThemeChange)
    
    // Load saved theme or apply default
    loadSavedTheme()
  })

  onUnmounted(() => {
    if (mediaQuery.value) {
      mediaQuery.value.removeEventListener('change', handleSystemThemeChange)
    }
  })

  return {
    currentTheme: readonly(currentTheme),
    availableThemes,
    currentColors,
    currentThemeInfo,
    setTheme
  }
}