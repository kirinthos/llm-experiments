"""
Obsidian Vault Integration Tools for MCP Server
Provides structured access to Obsidian note vaults
"""

import os
import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

# Obsidian-specific Pydantic models
class ObsidianVaultInput(BaseModel):
    vault_path: str = Field(..., description="Path to the Obsidian vault directory")

class ObsidianVaultOutput(BaseModel):
    success: bool = Field(..., description="Whether vault was found and accessible")
    vault_path: str = Field(..., description="Absolute path to the vault")
    vault_name: str = Field(..., description="Name of the vault")
    note_count: int = Field(..., description="Total number of notes in vault")
    attachment_count: int = Field(..., description="Number of attachments")
    config_exists: bool = Field(..., description="Whether .obsidian config exists")

class CreateNoteInput(BaseModel):
    vault_path: str = Field(..., description="Path to the Obsidian vault")
    note_name: str = Field(..., description="Name of the note (without .md extension)")
    content: str = Field("", description="Initial content of the note")
    frontmatter: Optional[Dict[str, Any]] = Field(None, description="YAML frontmatter as dictionary")
    folder: Optional[str] = Field(None, description="Subfolder to create note in")

class CreateNoteOutput(BaseModel):
    success: bool = Field(..., description="Whether note was created successfully")
    note_path: str = Field(..., description="Full path to the created note")
    note_name: str = Field(..., description="Name of the created note")
    has_frontmatter: bool = Field(..., description="Whether frontmatter was added")

class ReadNoteInput(BaseModel):
    vault_path: str = Field(..., description="Path to the Obsidian vault")
    note_name: str = Field(..., description="Name of the note to read")
    parse_frontmatter: bool = Field(True, description="Whether to parse YAML frontmatter")
    parse_links: bool = Field(True, description="Whether to extract wiki-links")

class ReadNoteOutput(BaseModel):
    success: bool = Field(..., description="Whether note was read successfully")
    note_path: str = Field(..., description="Full path to the note")
    content: str = Field(..., description="Raw content of the note")
    frontmatter: Optional[Dict[str, Any]] = Field(None, description="Parsed frontmatter")
    body: str = Field(..., description="Note content without frontmatter")
    word_count: int = Field(..., description="Word count of the note body")
    links: List[str] = Field(default_factory=list, description="Wiki-links found in note")
    tags: List[str] = Field(default_factory=list, description="Tags found in note")
    last_modified: str = Field(..., description="Last modification time")

class SearchNotesInput(BaseModel):
    vault_path: str = Field(..., description="Path to the Obsidian vault")
    query: str = Field(..., description="Search query (supports regex)")
    search_content: bool = Field(True, description="Search in note content")
    search_titles: bool = Field(True, description="Search in note titles")
    search_tags: bool = Field(False, description="Search in tags")
    case_sensitive: bool = Field(False, description="Case-sensitive search")
    limit: int = Field(50, description="Maximum number of results")

class AdvancedSearchInput(BaseModel):
    vault_path: str = Field(..., description="Path to the Obsidian vault")
    query: str = Field(..., description="Search query (supports full regex)")
    regex_mode: bool = Field(False, description="Enable full regex pattern matching")
    whole_words: bool = Field(False, description="Match whole words only")
    context_lines: int = Field(2, description="Number of context lines to show (0-5)")
    include_frontmatter: bool = Field(False, description="Search in YAML frontmatter")
    file_pattern: Optional[str] = Field(None, description="Glob pattern for files to include")
    exclude_pattern: Optional[str] = Field(None, description="Glob pattern for files to exclude")
    max_matches_per_file: int = Field(10, description="Maximum matches per file")
    case_sensitive: bool = Field(False, description="Case-sensitive search")
    limit: int = Field(100, description="Maximum number of files to search")

class AdvancedSearchOutput(BaseModel):
    success: bool = Field(..., description="Whether search completed successfully")
    query: str = Field(..., description="Search query used")
    search_stats: Dict[str, Any] = Field(..., description="Search statistics")
    matches: List[Dict[str, Any]] = Field(..., description="Detailed search results with context")

class SearchNotesOutput(BaseModel):
    success: bool = Field(..., description="Whether search completed successfully")
    query: str = Field(..., description="Search query used")
    total_matches: int = Field(..., description="Total number of matching notes")
    matches: List[Dict[str, Any]] = Field(..., description="List of matching notes with context")

class ListNotesInput(BaseModel):
    vault_path: str = Field(..., description="Path to the Obsidian vault")
    folder: Optional[str] = Field(None, description="Specific folder to list (None for all)")
    include_attachments: bool = Field(False, description="Include attachment files")
    sort_by: str = Field("name", description="Sort by: 'name', 'modified', 'created', 'size'")
    reverse: bool = Field(False, description="Reverse sort order")

class ListNotesOutput(BaseModel):
    success: bool = Field(..., description="Whether listing completed successfully")
    vault_path: str = Field(..., description="Path to the vault")
    folder: Optional[str] = Field(..., description="Folder that was listed")
    notes: List[Dict[str, Any]] = Field(..., description="List of notes with metadata")
    total_notes: int = Field(..., description="Total number of notes")

class UpdateNoteInput(BaseModel):
    vault_path: str = Field(..., description="Path to the Obsidian vault")
    note_name: str = Field(..., description="Name of the note to update")
    content: Optional[str] = Field(None, description="New content (None to keep existing)")
    frontmatter: Optional[Dict[str, Any]] = Field(None, description="New frontmatter")
    append_content: Optional[str] = Field(None, description="Content to append to note")
    prepend_content: Optional[str] = Field(None, description="Content to prepend to note")

class UpdateNoteOutput(BaseModel):
    success: bool = Field(..., description="Whether note was updated successfully")
    note_path: str = Field(..., description="Path to the updated note")
    changes_made: List[str] = Field(..., description="List of changes made")
    new_word_count: int = Field(..., description="Word count after update")

# Utility functions for Obsidian operations
def find_vault_config(vault_path: Path) -> bool:
    """Check if directory is a valid Obsidian vault"""
    return (vault_path / ".obsidian").exists()

def parse_frontmatter(content: str) -> tuple[Optional[Dict[str, Any]], str]:
    """Parse YAML frontmatter from note content"""
    if not content.startswith('---'):
        return None, content
    
    try:
        # Find end of frontmatter
        end_match = re.search(r'\n---\n', content)
        if not end_match:
            return None, content
        
        frontmatter_text = content[3:end_match.start()]
        body = content[end_match.end():]
        
        frontmatter = yaml.safe_load(frontmatter_text)
        return frontmatter, body
        
    except yaml.YAMLError:
        return None, content

def extract_links(content: str) -> List[str]:
    """Extract wiki-links from note content"""
    # Find [[link]] patterns
    wiki_links = re.findall(r'\[\[([^\]]+)\]\]', content)
    
    # Clean up links (remove aliases, etc.)
    clean_links = []
    for link in wiki_links:
        # Remove alias (text after |)
        if '|' in link:
            link = link.split('|')[0]
        clean_links.append(link.strip())
    
    return clean_links

def extract_tags(content: str) -> List[str]:
    """Extract tags from note content"""
    # Find #tag patterns
    tags = re.findall(r'#([a-zA-Z0-9_/-]+)', content)
    return list(set(tags))  # Remove duplicates

def create_frontmatter_string(frontmatter: Dict[str, Any]) -> str:
    """Create YAML frontmatter string"""
    return f"---\n{yaml.dump(frontmatter, default_flow_style=False)}---\n"

def find_note_path(vault_path: Path, note_name: str) -> Optional[Path]:
    """Find a note by name in the vault"""
    # Remove .md extension if provided
    if note_name.endswith('.md'):
        note_name = note_name[:-3]
    
    # Search for the note
    for note_path in vault_path.rglob(f"{note_name}.md"):
        return note_path
    
    return None

# Tool implementations
async def discover_obsidian_vault(input: ObsidianVaultInput) -> ObsidianVaultOutput:
    """Discover and analyze an Obsidian vault"""
    try:
        vault_path = Path(input.vault_path).expanduser().resolve()
        
        if not vault_path.exists():
            raise FileNotFoundError(f"Vault path not found: {vault_path}")
        
        if not vault_path.is_dir():
            raise ValueError(f"Path is not a directory: {vault_path}")
        
        # Check if it's a valid Obsidian vault
        config_exists = find_vault_config(vault_path)
        
        # Count notes and attachments
        note_count = len(list(vault_path.rglob("*.md")))
        
        # Common attachment extensions
        attachment_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf', '.mp3', '.mp4', '.mov'}
        attachment_count = 0
        
        for ext in attachment_extensions:
            attachment_count += len(list(vault_path.rglob(f"*{ext}")))
        
        return ObsidianVaultOutput(
            success=True,
            vault_path=str(vault_path),
            vault_name=vault_path.name,
            note_count=note_count,
            attachment_count=attachment_count,
            config_exists=config_exists
        )
        
    except Exception as e:
        return ObsidianVaultOutput(
            success=False,
            vault_path=input.vault_path,
            vault_name="",
            note_count=0,
            attachment_count=0,
            config_exists=False
        )

async def create_obsidian_note(input: CreateNoteInput) -> CreateNoteOutput:
    """Create a new note in the Obsidian vault"""
    try:
        vault_path = Path(input.vault_path).expanduser().resolve()
        
        if not vault_path.exists():
            raise FileNotFoundError(f"Vault not found: {vault_path}")
        
        # Determine note path
        if input.folder:
            note_dir = vault_path / input.folder
            note_dir.mkdir(parents=True, exist_ok=True)
        else:
            note_dir = vault_path
        
        # Remove .md extension if provided
        note_name = input.note_name
        if note_name.endswith('.md'):
            note_name = note_name[:-3]
        
        note_path = note_dir / f"{note_name}.md"
        
        # Check if note already exists
        if note_path.exists():
            raise FileExistsError(f"Note already exists: {note_path}")
        
        # Build note content
        content_parts = []
        has_frontmatter = False
        
        # Add frontmatter if provided
        if input.frontmatter:
            content_parts.append(create_frontmatter_string(input.frontmatter))
            has_frontmatter = True
        
        # Add content
        content_parts.append(input.content)
        
        full_content = '\n'.join(content_parts)
        
        # Write note
        note_path.write_text(full_content, encoding='utf-8')
        
        return CreateNoteOutput(
            success=True,
            note_path=str(note_path),
            note_name=note_name,
            has_frontmatter=has_frontmatter
        )
        
    except Exception as e:
        return CreateNoteOutput(
            success=False,
            note_path="",
            note_name=input.note_name,
            has_frontmatter=False
        )

async def read_obsidian_note(input: ReadNoteInput) -> ReadNoteOutput:
    """Read and parse an Obsidian note"""
    try:
        vault_path = Path(input.vault_path).expanduser().resolve()
        
        # Find the note
        note_path = find_note_path(vault_path, input.note_name)
        
        if not note_path:
            raise FileNotFoundError(f"Note not found: {input.note_name}")
        
        # Read note content
        content = note_path.read_text(encoding='utf-8')
        
        # Parse frontmatter
        frontmatter = None
        body = content
        
        if input.parse_frontmatter:
            frontmatter, body = parse_frontmatter(content)
        
        # Extract links and tags
        links = []
        tags = []
        
        if input.parse_links:
            links = extract_links(body)
            tags = extract_tags(body)
        
        # Get file stats
        stat = note_path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        # Count words
        word_count = len(body.split())
        
        return ReadNoteOutput(
            success=True,
            note_path=str(note_path),
            content=content,
            frontmatter=frontmatter,
            body=body,
            word_count=word_count,
            links=links,
            tags=tags,
            last_modified=last_modified
        )
        
    except Exception as e:
        return ReadNoteOutput(
            success=False,
            note_path="",
            content="",
            frontmatter=None,
            body="",
            word_count=0,
            links=[],
            tags=[],
            last_modified=""
        )

async def search_obsidian_notes(input: SearchNotesInput) -> SearchNotesOutput:
    """Search for notes in the Obsidian vault using ripgrep for performance"""
    import subprocess
    import json
    
    try:
        vault_path = Path(input.vault_path).expanduser().resolve()
        
        if not vault_path.exists():
            raise FileNotFoundError(f"Vault not found: {vault_path}")
        
        matches = []
        
        # Check if ripgrep is available
        try:
            subprocess.run(['rg', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Fallback to Python-based search if ripgrep not available
            return await _python_search_fallback(input)
        
        # Build ripgrep command
        rg_cmd = ['rg']
        
        # Case sensitivity
        if not input.case_sensitive:
            rg_cmd.append('--ignore-case')
        
        # Output format with line numbers and context
        rg_cmd.extend([
            '--json',  # JSON output for structured parsing
            '--with-filename',
            '--line-number',
            '--context', '1',  # 1 line of context before/after
            '--type', 'md',  # Only markdown files
        ])
        
        # Limit results
        if input.limit:
            rg_cmd.extend(['--max-count', str(input.limit)])
        
        # Add search pattern
        rg_cmd.append(input.query)
        
        # Add search directory
        rg_cmd.append(str(vault_path))
        
        # Execute ripgrep
        result = subprocess.run(
            rg_cmd,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Parse ripgrep JSON output
        if result.returncode == 0:
            current_file_matches = {}
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    rg_match = json.loads(line)
                    
                    if rg_match.get('type') == 'match':
                        data = rg_match['data']
                        file_path = Path(data['path']['text'])
                        
                        # Initialize file entry if not exists
                        file_key = str(file_path)
                        if file_key not in current_file_matches:
                            stat = file_path.stat()
                            
                            current_file_matches[file_key] = {
                                "note_name": file_path.stem,
                                "note_path": str(file_path),
                                "matches": [],
                                "total_matches": 0,
                                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "word_count": 0  # Will be calculated if needed
                            }
                        
                        # Add match context
                        match_text = data['lines']['text'].rstrip()
                        line_number = data['line_number']
                        
                        # Determine match type based on content
                        match_type = "content"
                        if line_number <= 10 and match_text.startswith('#'):
                            match_type = "heading"
                        elif match_text.strip().startswith('#') and not match_text.startswith('##'):
                            match_type = "tag"
                        
                        current_file_matches[file_key]["matches"].append({
                            "type": match_type,
                            "line_number": line_number,
                            "text": match_text,
                            "context": match_text[:200]  # First 200 chars
                        })
                        
                        current_file_matches[file_key]["total_matches"] += 1
                        
                except json.JSONDecodeError:
                    continue
            
            # Convert to list and add word counts for matched files
            for file_data in current_file_matches.values():
                try:
                    # Get word count for matched files
                    content = Path(file_data["note_path"]).read_text(encoding='utf-8')
                    _, body = parse_frontmatter(content)
                    file_data["word_count"] = len(body.split())
                except:
                    file_data["word_count"] = 0
                
                # Limit matches per file for display
                file_data["matches"] = file_data["matches"][:10]
                matches.append(file_data)
        
        # Additional searches based on input flags
        if input.search_titles:
            matches.extend(await _search_titles_with_rg(vault_path, input.query, input.case_sensitive))
        
        if input.search_tags:
            matches.extend(await _search_tags_with_rg(vault_path, input.query, input.case_sensitive))
        
        # Remove duplicates and limit results
        unique_matches = {}
        for match in matches:
            key = match["note_path"]
            if key not in unique_matches:
                unique_matches[key] = match
            else:
                # Merge matches from different search types
                existing = unique_matches[key]
                existing["matches"].extend(match["matches"])
                existing["total_matches"] += match["total_matches"]
                # Keep matches unique and limited
                existing["matches"] = existing["matches"][:10]
        
        final_matches = list(unique_matches.values())[:input.limit]
        
        return SearchNotesOutput(
            success=True,
            query=input.query,
            total_matches=len(final_matches),
            matches=final_matches
        )
        
    except subprocess.TimeoutExpired:
        return SearchNotesOutput(
            success=False,
            query=input.query,
            total_matches=0,
            matches=[],
        )
    except Exception as e:
        return SearchNotesOutput(
            success=False,
            query=input.query,
            total_matches=0,
            matches=[]
        )

async def _search_titles_with_rg(vault_path: Path, query: str, case_sensitive: bool) -> list:
    """Search note titles using ripgrep on filenames"""
    try:
        rg_cmd = ['rg', '--files', '--type', 'md']
        if not case_sensitive:
            rg_cmd.append('--ignore-case')
        
        rg_cmd.extend([query, str(vault_path)])
        
        result = subprocess.run(rg_cmd, capture_output=True, text=True, timeout=10)
        
        matches = []
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line:
                    file_path = Path(line)
                    if file_path.exists():
                        stat = file_path.stat()
                        matches.append({
                            "note_name": file_path.stem,
                            "note_path": str(file_path),
                            "matches": [{
                                "type": "title",
                                "text": file_path.stem,
                                "context": file_path.stem
                            }],
                            "total_matches": 1,
                            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "word_count": 0
                        })
        
        return matches
    except:
        return []

async def _search_tags_with_rg(vault_path: Path, query: str, case_sensitive: bool) -> list:
    """Search for tags using ripgrep with tag-specific pattern"""
    try:
        # Search for #tag pattern
        tag_pattern = f"#{query}" if not query.startswith('#') else query
        
        rg_cmd = ['rg', '--json', '--with-filename', '--line-number']
        if not case_sensitive:
            rg_cmd.append('--ignore-case')
        
        rg_cmd.extend(['--type', 'md', tag_pattern, str(vault_path)])
        
        result = subprocess.run(rg_cmd, capture_output=True, text=True, timeout=10)
        
        matches = []
        if result.returncode == 0:
            file_matches = {}
            
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                    
                try:
                    rg_match = json.loads(line)
                    if rg_match.get('type') == 'match':
                        data = rg_match['data']
                        file_path = Path(data['path']['text'])
                        
                        if str(file_path) not in file_matches:
                            stat = file_path.stat()
                            file_matches[str(file_path)] = {
                                "note_name": file_path.stem,
                                "note_path": str(file_path),
                                "matches": [],
                                "total_matches": 0,
                                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "word_count": 0
                            }
                        
                        match_text = data['lines']['text'].rstrip()
                        file_matches[str(file_path)]["matches"].append({
                            "type": "tag",
                            "line_number": data['line_number'],
                            "text": match_text,
                            "context": match_text
                        })
                        file_matches[str(file_path)]["total_matches"] += 1
                        
                except json.JSONDecodeError:
                    continue
            
            matches = list(file_matches.values())
        
        return matches
    except:
        return []

async def _python_search_fallback(input: SearchNotesInput) -> SearchNotesOutput:
    """Fallback Python-based search when ripgrep is not available"""
    try:
        vault_path = Path(input.vault_path).expanduser().resolve()
        matches = []
        flags = 0 if input.case_sensitive else re.IGNORECASE
        pattern = re.compile(input.query, flags)
        
        # Search through all markdown files
        for note_path in vault_path.rglob("*.md"):
            try:
                content = note_path.read_text(encoding='utf-8')
                frontmatter, body = parse_frontmatter(content)
                
                match_contexts = []
                
                # Search in title
                if input.search_titles:
                    if pattern.search(note_path.stem):
                        match_contexts.append({
                            "type": "title",
                            "text": note_path.stem,
                            "context": note_path.stem
                        })
                
                # Search in content
                if input.search_content:
                    for i, line in enumerate(body.split('\n'), 1):
                        if pattern.search(line):
                            match_contexts.append({
                                "type": "content",
                                "line_number": i,
                                "text": line.strip(),
                                "context": line.strip()[:200]
                            })
                
                # Search in tags
                if input.search_tags:
                    tags = extract_tags(content)
                    for tag in tags:
                        if pattern.search(tag):
                            match_contexts.append({
                                "type": "tag",
                                "text": tag,
                                "context": f"#{tag}"
                            })
                
                # If we found matches, add to results
                if match_contexts:
                    stat = note_path.stat()
                    
                    matches.append({
                        "note_name": note_path.stem,
                        "note_path": str(note_path),
                        "matches": match_contexts[:5],
                        "total_matches": len(match_contexts),
                        "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "word_count": len(body.split())
                    })
                
                # Limit total results
                if len(matches) >= input.limit:
                    break
                    
            except (UnicodeDecodeError, PermissionError):
                continue
        
        return SearchNotesOutput(
            success=True,
            query=input.query,
            total_matches=len(matches),
            matches=matches
        )
        
    except Exception as e:
        return SearchNotesOutput(
            success=False,
            query=input.query,
            total_matches=0,
            matches=[]
        )

async def advanced_search_obsidian_notes(input: AdvancedSearchInput) -> AdvancedSearchOutput:
    """Advanced search with full ripgrep features: regex, context, patterns"""
    import subprocess
    import json
    import time
    
    try:
        vault_path = Path(input.vault_path).expanduser().resolve()
        
        if not vault_path.exists():
            raise FileNotFoundError(f"Vault not found: {vault_path}")
        
        start_time = time.time()
        
        # Check if ripgrep is available
        try:
            subprocess.run(['rg', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return AdvancedSearchOutput(
                success=False,
                query=input.query,
                search_stats={"error": "ripgrep not available"},
                matches=[]
            )
        
        # Build advanced ripgrep command
        rg_cmd = ['rg']
        
        # Basic flags
        if not input.case_sensitive:
            rg_cmd.append('--ignore-case')
        
        # Regex mode
        if input.regex_mode:
            rg_cmd.append('--engine=regex')
        else:
            rg_cmd.append('--fixed-strings')  # Literal string search
        
        # Word boundaries
        if input.whole_words:
            rg_cmd.append('--word-regexp')
        
        # Context lines (clamped to 0-5)
        context_lines = max(0, min(5, input.context_lines))
        if context_lines > 0:
            rg_cmd.extend(['--context', str(context_lines)])
        
        # Output format
        rg_cmd.extend([
            '--json',
            '--with-filename',
            '--line-number',
            '--column',
            '--stats',  # Include search statistics
        ])
        
        # File type and patterns
        rg_cmd.extend(['--type', 'md'])
        
        if input.file_pattern:
            rg_cmd.extend(['--glob', input.file_pattern])
        
        if input.exclude_pattern:
            rg_cmd.extend(['--glob', f'!{input.exclude_pattern}'])
        
        # Limit matches per file
        if input.max_matches_per_file:
            rg_cmd.extend(['--max-count', str(input.max_matches_per_file)])
        
        # Search in frontmatter (by default ripgrep searches all content)
        # We'll filter frontmatter matches in post-processing if needed
        
        # Add search pattern and directory
        rg_cmd.append(input.query)
        rg_cmd.append(str(vault_path))
        
        # Execute ripgrep with timeout
        result = subprocess.run(
            rg_cmd,
            capture_output=True,
            text=True,
            timeout=60  # 1 minute timeout for complex searches
        )
        
        # Parse results
        matches = []
        search_stats = {}
        file_matches = {}
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                try:
                    rg_data = json.loads(line)
                    
                    # Handle statistics
                    if rg_data.get('type') == 'stats':
                        stats = rg_data['data']
                        search_stats = {
                            'files_searched': stats.get('searches', 0),
                            'files_with_matches': stats.get('searches_with_match', 0),
                            'total_matches': stats.get('matches', 0),
                            'bytes_searched': stats.get('bytes_searched', 0),
                            'search_time_ms': int((time.time() - start_time) * 1000)
                        }
                        continue
                    
                    # Handle matches
                    if rg_data.get('type') == 'match':
                        data = rg_data['data']
                        file_path = Path(data['path']['text'])
                        
                        # Initialize file entry
                        file_key = str(file_path)
                        if file_key not in file_matches:
                            try:
                                stat = file_path.stat()
                                
                                file_matches[file_key] = {
                                    'note_name': file_path.stem,
                                    'note_path': str(file_path),
                                    'relative_path': str(file_path.relative_to(vault_path)),
                                    'matches': [],
                                    'total_matches': 0,
                                    'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                    'file_size': stat.st_size
                                }
                            except:
                                continue
                        
                        # Process match data
                        line_number = data['line_number']
                        match_text = data['lines']['text'].rstrip()
                        
                        # Determine if this is in frontmatter
                        is_frontmatter = False
                        if line_number <= 20:  # Check first 20 lines for frontmatter
                            try:
                                content = file_path.read_text(encoding='utf-8')
                                if content.startswith('---'):
                                    frontmatter_end = content.find('\n---\n')
                                    if frontmatter_end > 0:
                                        frontmatter_lines = content[:frontmatter_end].count('\n')
                                        is_frontmatter = line_number <= frontmatter_lines + 1
                            except:
                                pass
                        
                        # Skip frontmatter matches if not requested
                        if is_frontmatter and not input.include_frontmatter:
                            continue
                        
                        # Determine match type
                        match_type = "content"
                        if is_frontmatter:
                            match_type = "frontmatter"
                        elif match_text.strip().startswith('#'):
                            if match_text.strip().startswith('##'):
                                match_type = "heading"
                            else:
                                match_type = "title"
                        elif match_text.strip().startswith('#') and ' ' not in match_text.strip():
                            match_type = "tag"
                        
                        # Extract column information for precise match highlighting
                        submatches = data.get('submatches', [])
                        highlighted_ranges = []
                        
                        for submatch in submatches:
                            highlighted_ranges.append({
                                'start': submatch['start'],
                                'end': submatch['end'],
                                'matched_text': submatch['match']['text']
                            })
                        
                        match_info = {
                            'type': match_type,
                            'line_number': line_number,
                            'column': data.get('column', 0),
                            'text': match_text,
                            'context': match_text[:300],  # Extended context
                            'highlighted_ranges': highlighted_ranges,
                            'is_frontmatter': is_frontmatter
                        }
                        
                        file_matches[file_key]['matches'].append(match_info)
                        file_matches[file_key]['total_matches'] += 1
                        
                except json.JSONDecodeError:
                    continue
            
            # Convert to final format and limit results
            matches = list(file_matches.values())[:input.limit]
            
            # Add word counts for matched files
            for file_data in matches:
                try:
                    content = Path(file_data['note_path']).read_text(encoding='utf-8')
                    _, body = parse_frontmatter(content)
                    file_data['word_count'] = len(body.split())
                    
                    # Add link and tag counts
                    file_data['link_count'] = len(extract_links(content))
                    file_data['tag_count'] = len(extract_tags(content))
                except:
                    file_data['word_count'] = 0
                    file_data['link_count'] = 0
                    file_data['tag_count'] = 0
        
        # Ensure we have search stats
        if not search_stats:
            search_stats = {
                'files_searched': len(list(vault_path.rglob('*.md'))),
                'files_with_matches': len(matches),
                'total_matches': sum(f['total_matches'] for f in matches),
                'search_time_ms': int((time.time() - start_time) * 1000)
            }
        
        return AdvancedSearchOutput(
            success=True,
            query=input.query,
            search_stats=search_stats,
            matches=matches
        )
        
    except subprocess.TimeoutExpired:
        return AdvancedSearchOutput(
            success=False,
            query=input.query,
            search_stats={'error': 'Search timed out after 60 seconds'},
            matches=[]
        )
    except Exception as e:
        return AdvancedSearchOutput(
            success=False,
            query=input.query,
            search_stats={'error': str(e)},
            matches=[]
        )

async def list_obsidian_notes(input: ListNotesInput) -> ListNotesOutput:
    """List all notes in the Obsidian vault"""
    try:
        vault_path = Path(input.vault_path).expanduser().resolve()
        
        if not vault_path.exists():
            raise FileNotFoundError(f"Vault not found: {vault_path}")
        
        # Determine search path
        if input.folder:
            search_path = vault_path / input.folder
            if not search_path.exists():
                raise FileNotFoundError(f"Folder not found: {input.folder}")
        else:
            search_path = vault_path
        
        notes = []
        
        # Find all markdown files
        pattern = "**/*.md" if input.folder is None else "*.md"
        
        for note_path in search_path.glob(pattern):
            try:
                stat = note_path.stat()
                
                # Basic file info
                note_info = {
                    "name": note_path.stem,
                    "path": str(note_path),
                    "relative_path": str(note_path.relative_to(vault_path)),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
                
                # Add word count
                try:
                    content = note_path.read_text(encoding='utf-8')
                    _, body = parse_frontmatter(content)
                    note_info["word_count"] = len(body.split())
                except:
                    note_info["word_count"] = 0
                
                notes.append(note_info)
                
            except (PermissionError, OSError):
                # Skip files we can't access
                continue
        
        # Sort notes
        sort_key_map = {
            "name": lambda x: x["name"].lower(),
            "modified": lambda x: x["modified"],
            "created": lambda x: x["created"],
            "size": lambda x: x["size"]
        }
        
        if input.sort_by in sort_key_map:
            notes.sort(key=sort_key_map[input.sort_by], reverse=input.reverse)
        
        return ListNotesOutput(
            success=True,
            vault_path=str(vault_path),
            folder=input.folder,
            notes=notes,
            total_notes=len(notes)
        )
        
    except Exception as e:
        return ListNotesOutput(
            success=False,
            vault_path=input.vault_path,
            folder=input.folder,
            notes=[],
            total_notes=0
        )