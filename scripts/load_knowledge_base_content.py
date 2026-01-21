#!/usr/bin/env python3
"""
Load knowledge base content (questions and techniques) from markdown files into database.

Usage:
    python scripts/load_knowledge_base_content.py --category questions
    python scripts/load_knowledge_base_content.py --category techniques
    python scripts/load_knowledge_base_content.py --category all
"""
import asyncio
import argparse
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any

import os
from sqlalchemy import select, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from contextlib import asynccontextmanager

# Import models  
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.models import QuestionTemplate
from src.db.database import Base


def parse_markdown_file(file_path: Path) -> Dict[str, Any]:
    """
    Parse markdown file with YAML frontmatter.
    
    Returns:
        dict with 'metadata' and 'content' keys
    """
    content = file_path.read_text(encoding='utf-8')
    
    # Extract YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not frontmatter_match:
        print(f"Warning: No frontmatter in {file_path}")
        return {'metadata': {}, 'content': content}
    
    metadata_str, markdown_content = frontmatter_match.groups()
    metadata = yaml.safe_load(metadata_str)
    
    return {'metadata': metadata, 'content': markdown_content}


def extract_questions_by_language(content: str) -> Dict[str, List[str]]:
    """
    Extract questions from markdown grouped by language.
    
    Returns:
        dict: {'ru': [...], 'en': [...], 'uk': [...]}
    """
    questions = {'ru': [], 'en': [], 'uk': [], 'es': [], 'de': []}
    
    # Split by language sections
    sections = re.split(r'\n## (RU|EN|UK|ES|DE):', content)
    
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            lang = sections[i].lower()
            section_content = sections[i + 1]
            
            # Extract numbered questions (1. ..., 2. ..., etc.)
            pattern = r'^\d+\.\s+(.+?)(?=\n\d+\.|$)'
            matches = re.findall(pattern, section_content, re.MULTILINE)
            
            if matches:
                questions[lang].extend([q.strip() for q in matches])
    
    return questions


def is_formal_question(text: str) -> bool:
    """
    Determine if question uses formal address (Вы/Ви) vs informal (ты/ти).
    
    For Russian/Ukrainian: checks for Вы/Ви forms.
    For other languages: defaults to False (informal).
    """
    # Russian formal markers
    formal_markers_ru = [
        r'\bВы\b', r'\bВас\b', r'\bВам\b', r'\bВами\b',
        r'\bрасскажите\b', r'\bподелитесь\b', r'\bвспомните\b'
    ]
    
    # Ukrainian formal markers  
    formal_markers_uk = [
        r'\bВи\b', r'\bВас\b', r'\bВам\b', r'\bВами\b',
        r'\bрозкажіть\b', r'\bподілі​ться\b', r'\bзгадайте\b'
    ]
    
    all_markers = formal_markers_ru + formal_markers_uk
    
    for marker in all_markers:
        if re.search(marker, text, re.IGNORECASE):
            return True
    
    return False


async def load_questions_from_file(file_path: Path, category: str = "expansion") -> int:
    """
    Load questions from a single markdown file into database.
    
    Returns:
        Number of questions loaded
    """
    print(f"\nProcessing: {file_path.name}")
    
    parsed = parse_markdown_file(file_path)
    metadata = parsed['metadata']
    content = parsed['content']
    
    questions_by_lang = extract_questions_by_language(content)
    
    total_loaded = 0
    
    async with get_db_session() as session:
        for lang, questions in questions_by_lang.items():
            if not questions:
                continue
            
            print(f"  {lang.upper()}: {len(questions)} questions")
            
            for question_text in questions:
                # Determine formality
                formal = is_formal_question(question_text)
                
                # Check if question already exists
                result = await session.execute(
                    select(QuestionTemplate)
                    .where(QuestionTemplate.template_text == question_text)
                    .where(QuestionTemplate.language_code == lang)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"    Skip (exists): {question_text[:50]}...")
                    continue
                
                # Create new question template
                question_template = QuestionTemplate(
                    language_code=lang,
                    formal=formal,
                    template_text=question_text,
                    category=category
                )
                session.add(question_template)
                total_loaded += 1
        
        await session.commit()
    
    return total_loaded


async def load_category(category: str, base_dir: Path) -> int:
    """
    Load all markdown files from a category directory.
    
    Args:
        category: 'questions' or 'techniques'
        base_dir: Base knowledge_base directory
        
    Returns:
        Total number of items loaded
    """
    category_dir = base_dir / category
    
    if not category_dir.exists():
        print(f"Error: Directory not found: {category_dir}")
        return 0
    
    markdown_files = list(category_dir.glob("*.md"))
    
    if not markdown_files:
        print(f"No markdown files found in {category_dir}")
        return 0
    
    print(f"\n{'='*60}")
    print(f"Loading {category.upper()} from {category_dir}")
    print(f"Found {len(markdown_files)} markdown files")
    print(f"{'='*60}")
    
    total_loaded = 0
    
    for file_path in sorted(markdown_files):
        loaded = await load_questions_from_file(file_path, category=category)
        total_loaded += loaded
    
    return total_loaded


@asynccontextmanager
async def get_db_session():
    """Simple database session for script usage."""
    # Get DB URL from environment or use default
    db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/mindsethappybot')
    
    engine = create_async_engine(db_url, echo=False)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def main():
    parser = argparse.ArgumentParser(
        description="Load knowledge base content into database"
    )
    parser.add_argument(
        '--category',
        choices=['questions', 'techniques', 'all'],
        default='all',
        help='Category to load (default: all)'
    )
    parser.add_argument(
        '--base-dir',
        type=Path,
        default=Path('knowledge_base'),
        help='Base directory for knowledge base files'
    )
    
    args = parser.parse_args()
    
    total_loaded = 0
    
    if args.category in ['questions', 'all']:
        loaded = await load_category('questions', args.base_dir)
        total_loaded += loaded
    
    if args.category in ['techniques', 'all']:
        loaded = await load_category('techniques', args.base_dir)
        total_loaded += loaded
    
    print(f"\n{'='*60}")
    print(f"✅ COMPLETED: Loaded {total_loaded} items total")
    print(f"{'='*60}")


if __name__ == '__main__':
    asyncio.run(main())
