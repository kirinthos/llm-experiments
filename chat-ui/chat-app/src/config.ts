/**
 * Frontend Configuration
 * Loads configuration from TOML file via API or uses defaults
 */

export interface ServerConfig {
  apiHost: string;
  apiPort: number;
  apiUrl: string;
  frontendHost: string;
  frontendPort: number;
  frontendUrl: string;
  healthCheckTimeout: number;
  healthCheckInterval: number;
}

export interface UIConfig {
  theme: 'auto' | 'light' | 'dark';
  autoRefreshStatus: boolean;
  showDebugInfo: boolean;
}

export interface AppConfig {
  server: ServerConfig;
  ui: UIConfig;
}

// Default configuration (fallback)
const DEFAULT_CONFIG: AppConfig = {
  server: {
    apiHost: 'localhost',
    apiPort: 4090,
    apiUrl: 'http://localhost:4090',
    frontendHost: 'localhost', 
    frontendPort: 4091,
    frontendUrl: 'http://localhost:4091',
    healthCheckTimeout: 5000,
    healthCheckInterval: 30
  },
  ui: {
    theme: 'auto',
    autoRefreshStatus: true,
    showDebugInfo: false
  }
};

class ConfigManager {
  private config: AppConfig = DEFAULT_CONFIG;
  private loaded = false;

  async loadConfig(): Promise<AppConfig> {
    if (this.loaded) {
      return this.config;
    }

    try {
      // Try to load config from API server
      const response = await fetch(`${DEFAULT_CONFIG.server.apiUrl}/config`, {
        timeout: 3000
      } as RequestInit);
      
      if (response.ok) {
        const serverConfig = await response.json();
        this.config = this.mergeConfigs(DEFAULT_CONFIG, serverConfig);
        console.log('✅ Configuration loaded from API server');
      } else {
        console.warn('⚠️ Could not load config from API, using defaults');
      }
    } catch (error) {
      console.warn('⚠️ Failed to load config from API, using defaults:', error);
    }

    // Override API URL if we're running on a different port
    const currentPort = window.location.port;
    if (currentPort && currentPort !== '4091') {
      // Assume API is on port 4090 if frontend is on a different port
      this.config.server.apiUrl = `http://localhost:4090`;
    }

    this.loaded = true;
    return this.config;
  }

  private mergeConfigs(defaultConfig: AppConfig, serverConfig: any): AppConfig {
    return {
      server: {
        ...defaultConfig.server,
        ...serverConfig.server
      },
      ui: {
        ...defaultConfig.ui,
        ...serverConfig.ui
      }
    };
  }

  getConfig(): AppConfig {
    return this.config;
  }

  getApiUrl(): string {
    return this.config.server.apiUrl;
  }

  getFrontendUrl(): string {
    return this.config.server.frontendUrl;
  }

  getHealthCheckInterval(): number {
    return this.config.server.healthCheckInterval * 1000; // Convert to milliseconds
  }

  getHealthCheckTimeout(): number {
    return this.config.server.healthCheckTimeout;
  }

  isDebugMode(): boolean {
    return this.config.ui.showDebugInfo;
  }

  shouldAutoRefreshStatus(): boolean {
    return this.config.ui.autoRefreshStatus;
  }
}

// Global config manager instance
const configManager = new ConfigManager();

export { configManager };

// Export convenience functions
export const loadConfig = () => configManager.loadConfig();
export const getConfig = () => configManager.getConfig();
export const getApiUrl = () => configManager.getApiUrl();
export const getFrontendUrl = () => configManager.getFrontendUrl();