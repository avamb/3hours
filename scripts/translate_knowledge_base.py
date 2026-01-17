#!/usr/bin/env python3
"""
MINDSETHAPPYBOT - Knowledge Base Auto-Translator
Translates markdown documents to 26 European languages using GPT-4

Usage:
    python scripts/translate_knowledge_base.py --languages de,fr,es --dry-run
    python scripts/translate_knowledge_base.py --tier 2  # Translate Tier 1-2 (9 langs)
    python scripts/translate_knowledge_base.py --all     # All 26 languages
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
import argparse
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import AsyncOpenAI
from src.config import get_settings
from src.utils.localization_config import SUPPORTED_LANGUAGES, LANGUAGE_NAMES

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Language Tiers for phased rollout
LANGUAGE_TIERS = {
    "tier1": ["ru", "en", "uk"],  # Core - already done
    "tier2": ["de", "fr", "es", "it", "pt", "nl"],  # Major Western Europe
    "tier3": ["sv", "da", "no", "fi", "is"],  # Northern Europe
    "tier4": ["pl", "cs", "sk", "hu"],  # Central Europe
    "tier5": ["el", "hr", "sl"],  # Southern Europe
    "tier6": ["ro", "bg", "lt", "lv", "et"],  # Eastern Europe & Baltic
}


class KnowledgeBaseTranslator:
    """Translates knowledge base documents using GPT-4"""

    def __init__(self, source_lang: str = "en", kb_dir: str = "knowledge_base"):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.source_lang = source_lang
        self.kb_dir = Path(kb_dir)
        self.translated_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
    def get_language_name(self, lang_code: str) -> str:
        """Get human-readable language name"""
        return LANGUAGE_NAMES.get(lang_code, lang_code)
    
    async def translate_text(
        self, 
        text: str, 
        target_lang: str,
        context: Optional[str] = None
    ) -> Optional[str]:
        """
        Translate text to target language using GPT-4.
        Preserves markdown formatting and YAML frontmatter.
        
        Args:
            text: Text to translate
            target_lang: Target language code
            context: Optional context about the content type
            
        Returns:
            Translated text or None on error
        """
        target_lang_name = self.get_language_name(target_lang)
        
        # Build translation prompt
        system_prompt = f"""You are a professional translator specializing in mental health and psychology content.

Translate the following text to {target_lang_name} ({target_lang}).

IMPORTANT RULES:
1. Preserve all markdown formatting (headers, lists, bold, italic, links)
2. Preserve YAML frontmatter exactly (the part between --- markers)
3. Translate content naturally, not word-by-word
4. Adapt cultural references appropriately for {target_lang_name} audience
5. Keep the same warm, empathetic tone
6. Translate examples to be relevant for {target_lang_name} culture
7. Keep technical terms (like "5-4-3-2-1 technique") in original + add translation in parentheses

OUTPUT:
- Only the translated text
- No explanations or comments
- Preserve original structure 100%"""

        if context:
            system_prompt += f"\n\nContent type: {context}"

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",  # or gpt-4-turbo for cheaper
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
                max_tokens=4000,
            )
            
            translated = response.choices[0].message.content.strip()
            
            # Log token usage
            if response.usage:
                logger.debug(
                    f"Translation tokens: {response.usage.total_tokens} "
                    f"(in: {response.usage.prompt_tokens}, out: {response.usage.completion_tokens})"
                )
            
            return translated
            
        except Exception as e:
            logger.error(f"Translation failed to {target_lang}: {e}")
            return None
    
    def scan_source_files(self) -> List[Path]:
        """
        Scan source language directory for markdown files.
        
        Returns:
            List of markdown file paths
        """
        source_dir = self.kb_dir / self.source_lang
        
        if not source_dir.exists():
            logger.error(f"Source directory not found: {source_dir}")
            return []
        
        md_files = list(source_dir.rglob("*.md"))
        
        # Filter out README and system files
        md_files = [
            f for f in md_files 
            if f.name.lower() not in ['readme.md', 'rag_system_master_instructions.md']
        ]
        
        return sorted(md_files)
    
    async def translate_file(
        self, 
        source_file: Path, 
        target_lang: str,
        dry_run: bool = False
    ) -> bool:
        """
        Translate a single file to target language.
        
        Args:
            source_file: Source markdown file
            target_lang: Target language code
            dry_run: If True, don't write files
            
        Returns:
            True if successful, False otherwise
        """
        # Determine target file path
        rel_path = source_file.relative_to(self.kb_dir / self.source_lang)
        target_file = self.kb_dir / target_lang / rel_path
        
        # Check if already translated
        if target_file.exists():
            logger.info(f"⏭️  Skipping existing: {target_file}")
            self.skipped_count += 1
            return True
        
        try:
            # Read source content
            content = source_file.read_text(encoding='utf-8')
            
            # Extract context from filename
            context = f"Mental health support content from file: {source_file.name}"
            
            # Translate
            logger.info(f"🔄 Translating: {source_file.name} → {target_lang}")
            translated = await self.translate_text(content, target_lang, context)
            
            if not translated:
                logger.error(f"❌ Translation failed: {source_file.name}")
                self.error_count += 1
                return False
            
            if dry_run:
                logger.info(f"✅ [DRY RUN] Would write to: {target_file}")
                logger.debug(f"Preview (first 200 chars):\n{translated[:200]}...")
                self.translated_count += 1
                return True
            
            # Create target directory
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write translated content
            target_file.write_text(translated, encoding='utf-8')
            
            logger.info(f"✅ Translated: {target_file}")
            self.translated_count += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Error processing {source_file}: {e}")
            self.error_count += 1
            return False
    
    async def translate_to_languages(
        self, 
        target_languages: List[str],
        dry_run: bool = False,
        max_concurrent: int = 3
    ) -> Dict[str, int]:
        """
        Translate all source files to multiple target languages.
        
        Args:
            target_languages: List of target language codes
            dry_run: If True, don't write files
            max_concurrent: Max concurrent translations
            
        Returns:
            Dict with statistics
        """
        source_files = self.scan_source_files()
        
        if not source_files:
            logger.error("No source files found!")
            return {"files": 0, "translated": 0, "skipped": 0, "errors": 0}
        
        logger.info(f"\n📚 Found {len(source_files)} source files in '{self.source_lang}'")
        logger.info(f"🎯 Target languages: {', '.join(target_languages)}")
        logger.info(f"🔄 Total translations needed: {len(source_files) * len(target_languages)}")
        
        if dry_run:
            logger.info(f"\n🔍 DRY RUN MODE - No files will be written\n")
        
        # Translate to each language
        for target_lang in target_languages:
            if target_lang == self.source_lang:
                logger.info(f"⏭️  Skipping source language: {target_lang}")
                continue
            
            logger.info(f"\n{'='*60}")
            logger.info(f"🌍 Translating to: {self.get_language_name(target_lang)} ({target_lang})")
            logger.info(f"{'='*60}\n")
            
            # Translate files with concurrency limit
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def translate_with_semaphore(file_path):
                async with semaphore:
                    return await self.translate_file(file_path, target_lang, dry_run)
            
            tasks = [translate_with_semaphore(f) for f in source_files]
            await asyncio.gather(*tasks)
        
        # Summary
        logger.info(f"\n" + "="*60)
        logger.info(f"📊 TRANSLATION SUMMARY")
        logger.info(f"="*60)
        logger.info(f"  Translated: {self.translated_count}")
        logger.info(f"  Skipped: {self.skipped_count}")
        logger.info(f"  Errors: {self.error_count}")
        logger.info(f"  Total: {len(source_files) * len(target_languages)}")
        
        return {
            "files": len(source_files),
            "languages": len(target_languages),
            "translated": self.translated_count,
            "skipped": self.skipped_count,
            "errors": self.error_count,
        }


async def main():
    parser = argparse.ArgumentParser(description='Translate knowledge base to multiple languages')
    parser.add_argument('--source', default='en', help='Source language (default: en)')
    parser.add_argument('--languages', help='Comma-separated language codes (e.g., de,fr,es)')
    parser.add_argument('--tier', type=int, choices=[1, 2, 3, 4, 5, 6], help='Translate up to tier N')
    parser.add_argument('--all', action='store_true', help='Translate to all 26 languages')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing files')
    parser.add_argument('--kb-dir', default='knowledge_base', help='Knowledge base directory')
    parser.add_argument('--concurrent', type=int, default=3, help='Max concurrent translations')
    
    args = parser.parse_args()
    
    # Determine target languages
    target_languages = []
    
    if args.languages:
        target_languages = [lang.strip() for lang in args.languages.split(',')]
    elif args.tier:
        # Include all tiers up to specified tier
        for tier_num in range(1, args.tier + 1):
            tier_key = f"tier{tier_num}"
            target_languages.extend(LANGUAGE_TIERS[tier_key])
    elif args.all:
        target_languages = SUPPORTED_LANGUAGES
    else:
        # Default: Tier 1-2 (9 core languages)
        target_languages = LANGUAGE_TIERS["tier1"] + LANGUAGE_TIERS["tier2"]
    
    # Remove duplicates and source language
    target_languages = [lang for lang in set(target_languages) if lang != args.source]
    
    if not target_languages:
        logger.error("No target languages specified!")
        logger.info("\nUsage examples:")
        logger.info("  python scripts/translate_knowledge_base.py --tier 2       # Core 9 languages")
        logger.info("  python scripts/translate_knowledge_base.py --languages de,fr,es")
        logger.info("  python scripts/translate_knowledge_base.py --all         # All 26 languages")
        return
    
    # Run translator
    logger.info("="*60)
    logger.info("MINDSETHAPPYBOT - Knowledge Base Translator")
    logger.info("="*60)
    
    translator = KnowledgeBaseTranslator(
        source_lang=args.source,
        kb_dir=args.kb_dir
    )
    
    stats = await translator.translate_to_languages(
        target_languages=target_languages,
        dry_run=args.dry_run,
        max_concurrent=args.concurrent
    )
    
    # Estimate cost
    if not args.dry_run and stats['translated'] > 0:
        # Rough estimate: ~1500 tokens per doc, $0.01 per 1K tokens for GPT-4
        estimated_tokens = stats['translated'] * 1500
        estimated_cost = (estimated_tokens / 1000) * 0.01
        
        logger.info(f"\n💰 Estimated cost: ${estimated_cost:.2f}")
        logger.info(f"   (Actual cost may vary based on document length)")
    
    if args.dry_run:
        logger.info(f"\n🔍 DRY RUN completed. Run without --dry-run to actually translate.")
    else:
        logger.info(f"\n🎉 Translation complete!")
        logger.info(f"\n📝 Next steps:")
        logger.info(f"  1. Review translated files in knowledge_base/<lang>/")
        logger.info(f"  2. Load into database: python scripts/load_knowledge_base_content.py")
        logger.info(f"  3. Index: python -m src.knowledge_indexer")


if __name__ == "__main__":
    asyncio.run(main())
