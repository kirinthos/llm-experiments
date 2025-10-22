#!/usr/bin/env python3
"""
Configuration Loader for Universal AI Chat
Loads TOML configuration and provides typed access to settings
"""

import os
import toml
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ServerConfig:
    api_host: str
    api_port: int
    api_url: str
    frontend_host: str
    frontend_port: int
    frontend_url: str
    health_check_timeout: int
    health_check_interval: int

@dataclass
class ModelProviderConfig:
    enabled: bool
    models: List[str]

@dataclass
class ModelsConfig:
    default_provider: str
    default_model: str
    max_tokens_default: int
    temperature_default: float
    openai: ModelProviderConfig
    gemini: ModelProviderConfig

@dataclass
class MCPConfig:
    enabled: bool
    tools_timeout: int
    max_tools: int

@dataclass
class UIConfig:
    theme: str
    auto_refresh_status: bool
    show_debug_info: bool

@dataclass
class LoggingConfig:
    level: str
    file: str
    max_size: str
    backup_count: int

@dataclass
class SecurityConfig:
    enable_cors: bool
    allowed_hosts: List[str]
    max_connections: int

@dataclass
class APIConfig:
    cors_origins: List[str]
    max_request_size: str
    request_timeout: int

@dataclass
class DevelopmentConfig:
    auto_restart: bool
    debug_mode: bool
    log_level: str

@dataclass
class AppConfig:
    server: ServerConfig
    models: ModelsConfig
    mcp: MCPConfig
    ui: UIConfig
    logging: LoggingConfig
    security: SecurityConfig
    api: APIConfig
    development: DevelopmentConfig

class ConfigLoader:
    """Configuration loader with validation and type safety"""
    
    def __init__(self, config_path: str = "config.toml"):
        self.config_path = Path(config_path)
        
        # If config doesn't exist in current dir, try parent directory
        if not self.config_path.exists():
            parent_config = Path("../config.toml")
            if parent_config.exists():
                self.config_path = parent_config
        
        self._config_data: Optional[Dict[str, Any]] = None
        self._app_config: Optional[AppConfig] = None
    
    def load(self) -> AppConfig:
        """Load and parse the TOML configuration file"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                self._config_data = toml.load(f)
            
            self._app_config = self._parse_config(self._config_data)
            return self._app_config
        
        except toml.TomlDecodeError as e:
            raise ValueError(f"Invalid TOML syntax in {self.config_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
    
    def _parse_config(self, data: Dict[str, Any]) -> AppConfig:
        """Parse raw config data into typed configuration objects"""
        
        # Server configuration
        server_data = data.get('server', {})
        server = ServerConfig(
            api_host=server_data.get('api_host', 'localhost'),
            api_port=server_data.get('api_port', 4090),
            api_url=server_data.get('api_url', 'http://localhost:4090'),
            frontend_host=server_data.get('frontend_host', 'localhost'),
            frontend_port=server_data.get('frontend_port', 4091),
            frontend_url=server_data.get('frontend_url', 'http://localhost:4091'),
            health_check_timeout=server_data.get('health_check_timeout', 5000),
            health_check_interval=server_data.get('health_check_interval', 30)
        )
        
        # Models configuration
        models_data = data.get('models', {})
        openai_data = models_data.get('openai', {})
        gemini_data = models_data.get('gemini', {})
        
        models = ModelsConfig(
            default_provider=models_data.get('default_provider', 'openai'),
            default_model=models_data.get('default_model', 'gpt-4o-mini'),
            max_tokens_default=models_data.get('max_tokens_default', 1000),
            temperature_default=models_data.get('temperature_default', 0.7),
            openai=ModelProviderConfig(
                enabled=openai_data.get('enabled', True),
                models=openai_data.get('models', ['gpt-4o-mini'])
            ),
            gemini=ModelProviderConfig(
                enabled=gemini_data.get('enabled', True),
                models=gemini_data.get('models', ['gemini-2.5-flash'])
            )
        )
        
        # MCP configuration
        mcp_data = data.get('mcp', {})
        mcp = MCPConfig(
            enabled=mcp_data.get('enabled', True),
            tools_timeout=mcp_data.get('tools_timeout', 10),
            max_tools=mcp_data.get('max_tools', 50)
        )
        
        # UI configuration
        ui_data = data.get('ui', {})
        ui = UIConfig(
            theme=ui_data.get('theme', 'auto'),
            auto_refresh_status=ui_data.get('auto_refresh_status', True),
            show_debug_info=ui_data.get('show_debug_info', False)
        )
        
        # Logging configuration
        logging_data = data.get('logging', {})
        logging_config = LoggingConfig(
            level=logging_data.get('level', 'INFO'),
            file=logging_data.get('file', 'app.log'),
            max_size=logging_data.get('max_size', '10MB'),
            backup_count=logging_data.get('backup_count', 5)
        )
        
        # Security configuration
        security_data = data.get('security', {})
        security = SecurityConfig(
            enable_cors=security_data.get('enable_cors', True),
            allowed_hosts=security_data.get('allowed_hosts', ['localhost', '127.0.0.1']),
            max_connections=security_data.get('max_connections', 100)
        )
        
        # API configuration
        api_data = data.get('api', {})
        api = APIConfig(
            cors_origins=api_data.get('cors_origins', ['http://localhost:4091']),
            max_request_size=api_data.get('max_request_size', '16MB'),
            request_timeout=api_data.get('request_timeout', 30)
        )
        
        # Development configuration
        dev_data = data.get('development', {})
        development = DevelopmentConfig(
            auto_restart=dev_data.get('auto_restart', True),
            debug_mode=dev_data.get('debug_mode', False),
            log_level=dev_data.get('log_level', 'INFO')
        )
        
        return AppConfig(
            server=server,
            models=models,
            mcp=mcp,
            ui=ui,
            logging=logging_config,
            security=security,
            api=api,
            development=development
        )
    
    def get_api_url(self) -> str:
        """Get the API server URL"""
        if not self._app_config:
            self.load()
        return self._app_config.server.api_url
    
    def get_frontend_url(self) -> str:
        """Get the frontend server URL"""
        if not self._app_config:
            self.load()
        return self._app_config.server.frontend_url
    
    def get_all_models(self) -> List[Dict[str, str]]:
        """Get all enabled models in the format expected by the API"""
        if not self._app_config:
            self.load()
        
        models = []
        config = self._app_config.models
        
        if config.openai.enabled:
            for model_id in config.openai.models:
                models.append({
                    'id': model_id,
                    'name': self._format_model_name(model_id),
                    'provider': 'openai',
                    'description': f'OpenAI {self._format_model_name(model_id)} with MCP tool support'
                })
        
        if config.gemini.enabled:
            for model_id in config.gemini.models:
                models.append({
                    'id': model_id,
                    'name': self._format_model_name(model_id),
                    'provider': 'gemini',
                    'description': f'Google {self._format_model_name(model_id)} with MCP tool support'
                })
        
        return models
    
    def _format_model_name(self, model_id: str) -> str:
        """Format model ID into a human-readable name"""
        # Convert model IDs to readable names
        name_map = {
            'gpt-4o': 'GPT-4o',
            'gpt-4o-mini': 'GPT-4o Mini',
            'gpt-4-turbo': 'GPT-4 Turbo',
            'gpt-4': 'GPT-4',
            'gpt-3.5-turbo': 'GPT-3.5 Turbo',
            'gemini-2.5-flash': 'Gemini 2.5 Flash',
            'gemini-1.5-pro': 'Gemini 1.5 Pro',
            'gemini-1.5-flash': 'Gemini 1.5 Flash',
            'gemini-1.0-pro': 'Gemini 1.0 Pro',
            'gemini-1.0-ultra': 'Gemini 1.0 Ultra'
        }
        return name_map.get(model_id, model_id.title())
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        if not self._app_config:
            try:
                self.load()
            except Exception as e:
                return [f"Failed to load config: {e}"]
        
        config = self._app_config
        
        # Validate ports
        if config.server.api_port == config.server.frontend_port:
            issues.append("API and frontend ports cannot be the same")
        
        if not (1024 <= config.server.api_port <= 65535):
            issues.append(f"API port {config.server.api_port} is not in valid range (1024-65535)")
        
        if not (1024 <= config.server.frontend_port <= 65535):
            issues.append(f"Frontend port {config.server.frontend_port} is not in valid range (1024-65535)")
        
        # Validate models
        if not config.models.openai.enabled and not config.models.gemini.enabled:
            issues.append("At least one model provider must be enabled")
        
        # Validate default model exists
        all_models = [m['id'] for m in self.get_all_models()]
        if config.models.default_model not in all_models:
            issues.append(f"Default model '{config.models.default_model}' is not in enabled models")
        
        return issues

# Global config loader instance
_config_loader = None

def get_config() -> AppConfig:
    """Get the global configuration instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader.load()

def get_config_loader() -> ConfigLoader:
    """Get the global config loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

if __name__ == "__main__":
    # Test the configuration loader
    try:
        loader = ConfigLoader()
        config = loader.load()
        
        print("✅ Configuration loaded successfully!")
        print(f"📡 API Server: {config.server.api_url}")
        print(f"🎨 Frontend: {config.server.frontend_url}")
        print(f"🤖 Models: {len(loader.get_all_models())} available")
        print(f"🔧 MCP Enabled: {config.mcp.enabled}")
        
        # Validate configuration
        issues = loader.validate_config()
        if issues:
            print("\n⚠️  Configuration issues:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("\n✅ Configuration validation passed!")
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        exit(1)