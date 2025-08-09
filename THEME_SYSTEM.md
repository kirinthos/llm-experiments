# 🎨 Theme System Documentation

The Universal AI Chat application now includes a comprehensive, flexible theming
system that supports multiple themes and makes it easy to add new ones.

## 🌟 Features

- **4 Built-in Themes**: Light, Dark, System, and GNOME Pink
- **System Theme Detection**: Automatically follows OS dark/light mode
  preference
- **Persistent Preferences**: Theme choice saved in localStorage
- **Easy Theme Selector**: Floating button in lower-right corner with theme
  dropdown
- **Smooth Transitions**: Animated theme switching with CSS transitions
- **Extensible Architecture**: JSON-based configuration for easy theme additions

## 🎯 Available Themes

### 🌞 Light Theme

- Clean, bright interface with blue accents
- Optimal for well-lit environments
- High contrast for accessibility

### 🌙 Dark Theme

- Dark background with light text
- Reduced eye strain in low-light conditions
- Modern dark UI aesthetic

### 💻 System Theme

- Automatically follows OS preference
- Switches between light/dark based on system settings
- Updates in real-time when system preference changes

### 🌸 GNOME Pink Theme

- Inspired by GNOME 48's design language
- Pink accents (#c061cb) on dark gray background
- Modern, stylish appearance

## 🛠️ Architecture

### Core Components

1. **`themes.json`** - Theme configuration file
2. **`ThemeManager.ts`** - Core theme management logic
3. **`ThemeSelector.ts`** - UI component for theme selection
4. **CSS Custom Properties** - Dynamic theming via CSS variables

### File Structure

```
src/
├── themes.json              # Theme definitions
├── utils/
│   └── themeManager.ts      # Theme management logic
├── components/
│   └── ThemeSelector.ts     # Theme selector UI
└── style.css               # CSS with theme variables
```

## 🎨 Adding New Themes

### Step 1: Define Theme in JSON

Add your theme to `src/themes.json`:

```json
{
  "themes": {
    "your-theme-name": {
      "name": "Your Theme Name",
      "icon": "🎨",
      "colors": {
        "primary": "#your-primary-color",
        "primaryHover": "#your-primary-hover",
        "secondary": "#your-secondary-color",
        "success": "#your-success-color",
        "warning": "#your-warning-color",
        "danger": "#your-danger-color",
        "info": "#your-info-color",
        "background": "#your-background",
        "surface": "#your-surface",
        "surfaceHover": "#your-surface-hover",
        "border": "#your-border",
        "text": "#your-text",
        "textSecondary": "#your-text-secondary",
        "textMuted": "#your-text-muted",
        "shadow": "rgba(0, 0, 0, 0.1)",
        "shadowHover": "rgba(0, 0, 0, 0.15)",
        "chatBubbleUser": "#your-user-bubble",
        "chatBubbleUserText": "#your-user-text",
        "chatBubbleAssistant": "#your-assistant-bubble",
        "chatBubbleAssistantText": "#your-assistant-text",
        "inputBackground": "#your-input-bg",
        "inputBorder": "#your-input-border",
        "inputFocus": "#your-input-focus"
      }
    }
  }
}
```

### Step 2: No Code Changes Needed!

The theme system automatically:

- ✅ Detects the new theme
- ✅ Adds it to the theme selector
- ✅ Applies the colors via CSS custom properties
- ✅ Persists the selection in localStorage

## 🎯 Theme Color Properties

| Property              | Purpose                 | Example            |
| --------------------- | ----------------------- | ------------------ |
| `primary`             | Main accent color       | Buttons, links     |
| `primaryHover`        | Hover state for primary | Button hover       |
| `background`          | Main app background     | Body background    |
| `surface`             | Card/panel backgrounds  | Message containers |
| `surfaceHover`        | Hover states            | Button hover       |
| `text`                | Primary text color      | Main content       |
| `textSecondary`       | Secondary text          | Timestamps, labels |
| `chatBubbleUser`      | User message background | User chat bubbles  |
| `chatBubbleAssistant` | AI message background   | AI chat bubbles    |
| `inputBackground`     | Input field background  | Text input         |
| `inputFocus`          | Focus ring color        | Input focus state  |

## 🔧 Advanced Usage

### Programmatic Theme Control

```typescript
import { ThemeManager } from "./utils/themeManager";

const themeManager = new ThemeManager();

// Set theme
themeManager.setTheme("dark");

// Get current theme
const current = themeManager.getCurrentTheme();

// Listen for theme changes
themeManager.onThemeChange((themeId, colors) => {
  console.log("Theme changed to:", themeId);
  console.log("Colors:", colors);
});

// Get all available themes
const themes = themeManager.getAvailableThemes();
```

### Custom CSS with Theme Variables

```css
.my-component {
  background: var(--color-surface);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  transition: all 0.3s ease;
}

.my-component:hover {
  background: var(--color-surface-hover);
}
```

## 🎨 Theme Design Guidelines

### Color Accessibility

- Ensure sufficient contrast ratios (4.5:1 for normal text, 3:1 for large text)
- Test themes with color blindness simulators
- Provide clear visual hierarchy

### Consistency

- Use semantic color naming (primary, secondary, etc.)
- Maintain consistent spacing and sizing
- Follow platform conventions for dark/light themes

### Performance

- Use CSS custom properties for instant theme switching
- Minimize theme-specific assets
- Leverage CSS transitions for smooth changes

## 🚀 Usage in Application

The theme system is automatically initialized when the app starts:

1. **Theme Selector**: Click the floating button in the lower-right corner
2. **Theme Options**: Choose from Light, Dark, System, or GNOME Pink
3. **Automatic Persistence**: Your choice is saved and restored on next visit
4. **System Integration**: System theme follows OS preference automatically

## 🛠️ Development

### Testing Themes

1. Start the development server: `npm run dev`
2. Open the app in your browser
3. Click the theme selector button (🌙 icon in lower-right)
4. Test each theme for visual consistency

### Adding Theme-Specific Styles

If needed, you can add theme-specific CSS:

```css
/* Theme-specific overrides */
body.theme-gnome-pink .special-component {
  /* GNOME Pink specific styles */
}

body.theme-dark .special-component {
  /* Dark theme specific styles */
}
```

## 🎯 Future Enhancements

Potential improvements for the theme system:

- [ ] **More Built-in Themes**: High contrast, colorblind-friendly themes
- [ ] **Theme Import/Export**: Share custom themes
- [ ] **Theme Editor**: Visual theme customization tool
- [ ] **Accent Color Picker**: Customize primary color while keeping theme base
- [ ] **Automatic Theme Scheduling**: Time-based theme switching

---

**Happy Theming!** 🎨✨
