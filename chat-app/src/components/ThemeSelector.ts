import type { ThemeManager, ThemeId } from '../utils/themeManager.ts';

export class ThemeSelector {
  private element: HTMLElement;
  private themeManager: ThemeManager;
  private isOpen: boolean = false;

  constructor(themeManager: ThemeManager) {
    this.themeManager = themeManager;
    this.element = this.createElement();
    this.setupEventListeners();
  }

  private createElement(): HTMLElement {
    const container = document.createElement('div');
    container.className = 'theme-selector';
    container.innerHTML = `
      <button class="theme-selector-button" title="Change theme">
        <span class="theme-icon">🌙</span>
      </button>
      <div class="theme-dropdown">
        <div class="theme-options">
          ${this.createThemeOptions()}
        </div>
      </div>
    `;
    return container;
  }

  private createThemeOptions(): string {
    const themes = this.themeManager.getAvailableThemes();
    return themes.map(({ id, theme }) => `
      <button class="theme-option" data-theme="${id}">
        <span class="theme-option-icon">${theme.icon}</span>
        <span class="theme-option-name">${theme.name}</span>
      </button>
    `).join('');
  }

  private setupEventListeners(): void {
    const button = this.element.querySelector('.theme-selector-button') as HTMLButtonElement;

    // Toggle dropdown
    button.addEventListener('click', (e) => {
      e.stopPropagation();
      this.toggleDropdown();
    });

    // Handle theme selection
    this.element.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      const option = target.closest('.theme-option') as HTMLElement;
      if (option) {
        const themeId = option.dataset.theme as ThemeId;
        this.themeManager.setTheme(themeId);
        this.closeDropdown();
        this.updateButtonIcon();
      }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', () => {
      this.closeDropdown();
    });

    // Update button icon when theme changes
    this.themeManager.onThemeChange(() => {
      this.updateButtonIcon();
      this.updateActiveOption();
    });

    // Initial update
    this.updateButtonIcon();
    this.updateActiveOption();
  }

  private toggleDropdown(): void {
    if (this.isOpen) {
      this.closeDropdown();
    } else {
      this.openDropdown();
    }
  }

  private openDropdown(): void {
    this.isOpen = true;
    this.element.classList.add('open');
  }

  private closeDropdown(): void {
    this.isOpen = false;
    this.element.classList.remove('open');
  }

  private updateButtonIcon(): void {
    const currentTheme = this.themeManager.getCurrentTheme();
    const themes = this.themeManager.getAvailableThemes();
    const theme = themes.find(t => t.id === currentTheme);
    
    const iconElement = this.element.querySelector('.theme-icon') as HTMLElement;
    if (theme && iconElement) {
      iconElement.textContent = theme.theme.icon;
    }
  }

  private updateActiveOption(): void {
    const currentTheme = this.themeManager.getCurrentTheme();
    const options = this.element.querySelectorAll('.theme-option');
    
    options.forEach(option => {
      const htmlOption = option as HTMLElement;
      if (htmlOption.dataset.theme === currentTheme) {
        htmlOption.classList.add('active');
      } else {
        htmlOption.classList.remove('active');
      }
    });
  }

  public mount(parent: HTMLElement): void {
    parent.appendChild(this.element);
  }

  public unmount(): void {
    if (this.element.parentNode) {
      this.element.parentNode.removeChild(this.element);
    }
  }
}