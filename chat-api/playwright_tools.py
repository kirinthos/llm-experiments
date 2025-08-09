"""
Playwright tools for web automation through our AI agent
"""

import asyncio
import json
import base64
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
import os


class PlaywrightManager:
    """Manages Playwright browser instances and operations"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.headless = True
        
    async def start_browser(self, headless: bool = True, browser_type: str = "chromium"):
        """Start a browser instance"""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
        
        if self.browser is not None:
            await self.close_browser()
        
        self.headless = headless
        
        # Choose browser type
        if browser_type == "firefox":
            browser_launcher = self.playwright.firefox
        elif browser_type == "webkit":
            browser_launcher = self.playwright.webkit
        else:
            browser_launcher = self.playwright.chromium
        
        self.browser = await browser_launcher.launch(headless=headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        return "Browser started successfully"
    
    async def close_browser(self):
        """Close browser and cleanup"""
        if self.page:
            await self.page.close()
            self.page = None
        if self.context:
            await self.context.close()
            self.context = None
        if self.browser:
            await self.browser.close()
            self.browser = None
    
    async def navigate_to_url(self, url: str) -> str:
        """Navigate to a URL"""
        if not self.page:
            await self.start_browser()
        
        try:
            await self.page.goto(url)
            title = await self.page.title()
            return f"Successfully navigated to {url}. Page title: '{title}'"
        except Exception as e:
            return f"Failed to navigate to {url}: {str(e)}"
    
    async def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take a screenshot of the current page"""
        if not self.page:
            return "No page is currently open"
        
        try:
            if filename is None:
                filename = "screenshot.png"
            
            await self.page.screenshot(path=filename)
            return f"Screenshot saved as {filename}"
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"
    
    async def get_page_content(self) -> str:
        """Get the current page content"""
        if not self.page:
            return "No page is currently open"
        
        try:
            content = await self.page.content()
            return f"Page content retrieved ({len(content)} characters)"
        except Exception as e:
            return f"Failed to get page content: {str(e)}"
    
    async def get_page_text(self) -> str:
        """Get visible text from the current page"""
        if not self.page:
            return "No page is currently open"
        
        try:
            text = await self.page.inner_text('body')
            return f"Page text retrieved ({len(text)} characters): {text[:500]}..." if len(text) > 500 else text
        except Exception as e:
            return f"Failed to get page text: {str(e)}"
    
    async def click_element(self, selector: str) -> str:
        """Click an element by selector"""
        if not self.page:
            return "No page is currently open"
        
        try:
            await self.page.click(selector)
            return f"Successfully clicked element: {selector}"
        except Exception as e:
            return f"Failed to click element {selector}: {str(e)}"
    
    async def fill_input(self, selector: str, text: str) -> str:
        """Fill an input field"""
        if not self.page:
            return "No page is currently open"
        
        try:
            await self.page.fill(selector, text)
            return f"Successfully filled input {selector} with text"
        except Exception as e:
            return f"Failed to fill input {selector}: {str(e)}"
    
    async def wait_for_element(self, selector: str, timeout: int = 5000) -> str:
        """Wait for an element to appear"""
        if not self.page:
            return "No page is currently open"
        
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return f"Element {selector} appeared"
        except Exception as e:
            return f"Element {selector} did not appear within {timeout}ms: {str(e)}"
    
    async def get_element_text(self, selector: str) -> str:
        """Get text content of an element"""
        if not self.page:
            return "No page is currently open"
        
        try:
            text = await self.page.inner_text(selector)
            return f"Element text: {text}"
        except Exception as e:
            return f"Failed to get text from element {selector}: {str(e)}"


# Global manager instance
_playwright_manager = PlaywrightManager()


# Synchronous wrapper functions for our tools
def start_browser(headless: bool = True, browser_type: str = "chromium") -> str:
    """Start a browser instance"""
    return asyncio.run(_playwright_manager.start_browser(headless, browser_type))


def navigate_to_url(url: str) -> str:
    """Navigate to a URL and capture the page"""
    return asyncio.run(_playwright_manager.navigate_to_url(url))


def take_screenshot(filename: str = "screenshot.png") -> str:
    """Take a screenshot of the current page"""
    return asyncio.run(_playwright_manager.take_screenshot(filename))


def get_page_content() -> str:
    """Get the HTML content of the current page"""
    return asyncio.run(_playwright_manager.get_page_content())


def get_page_text() -> str:
    """Get visible text from the current page"""
    return asyncio.run(_playwright_manager.get_page_text())


def click_element(selector: str) -> str:
    """Click an element by CSS selector"""
    return asyncio.run(_playwright_manager.click_element(selector))


def fill_input(selector: str, text: str) -> str:
    """Fill an input field with text"""
    return asyncio.run(_playwright_manager.fill_input(selector, text))


def wait_for_element(selector: str, timeout: int = 5000) -> str:
    """Wait for an element to appear on the page"""
    return asyncio.run(_playwright_manager.wait_for_element(selector, timeout))


def get_element_text(selector: str) -> str:
    """Get text content of an element"""
    return asyncio.run(_playwright_manager.get_element_text(selector))


def close_browser() -> str:
    """Close the browser and cleanup"""
    asyncio.run(_playwright_manager.close_browser())
    return "Browser closed successfully"


# Tool schemas for the AI agent
PLAYWRIGHT_TOOL_SCHEMAS = {
    "start_browser": {
        "type": "object",
        "properties": {
            "headless": {
                "type": "boolean",
                "description": "Whether to run browser in headless mode (no GUI)",
                "default": True
            },
            "browser_type": {
                "type": "string",
                "enum": ["chromium", "firefox", "webkit"],
                "description": "Type of browser to launch",
                "default": "chromium"
            }
        },
        "required": []
    },
    
    "navigate_to_url": {
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The URL to navigate to (must include http:// or https://)"
            }
        },
        "required": ["url"]
    },
    
    "take_screenshot": {
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Filename for the screenshot (default: screenshot.png)",
                "default": "screenshot.png"
            }
        },
        "required": []
    },
    
    "get_page_content": {
        "type": "object",
        "properties": {},
        "required": []
    },
    
    "get_page_text": {
        "type": "object",
        "properties": {},
        "required": []
    },
    
    "click_element": {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector for the element to click"
            }
        },
        "required": ["selector"]
    },
    
    "fill_input": {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector for the input field"
            },
            "text": {
                "type": "string",
                "description": "Text to fill in the input field"
            }
        },
        "required": ["selector", "text"]
    },
    
    "wait_for_element": {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector for the element to wait for"
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in milliseconds (default: 5000)",
                "default": 5000
            }
        },
        "required": ["selector"]
    },
    
    "get_element_text": {
        "type": "object",
        "properties": {
            "selector": {
                "type": "string",
                "description": "CSS selector for the element to get text from"
            }
        },
        "required": ["selector"]
    },
    
    "close_browser": {
        "type": "object",
        "properties": {},
        "required": []
    }
}