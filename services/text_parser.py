import re
from typing import List, Dict, Optional


def parse_vocabulary_text(text: str) -> List[Dict]:
    """
    Parse text containing vocabulary entries in various formats.
    
    Supported formats:
    1. Word /phonetic/: Translation
    2. Word /phonetic/: Translation (extra context)
    3. "Example sentence" (Translation)
    
    Returns list of vocabulary items with word, phonetic, translation, example_en, example_vi
    """
    results = []
    lines = text.strip().split('\n')
    
    # Pattern for vocabulary: Word /phonetic/: Translation
    # Examples:
    # Self-invocation /self ɪnvəˈkeɪʃn/: Tự gọi chính mình.
    # Bypass /baɪˈpæs/: Bỏ qua, đi vòng qua (Bypass the proxy).
    vocab_pattern = re.compile(
        r'^([A-Za-z][\w\s\-\']+?)\s*'  # Word (starts with letter, can have spaces/hyphens)
        r'/([^/]+)/\s*'                 # /phonetic/
        r'[:\-–]\s*'                    # separator (: or - or –)
        r'(.+)$',                       # Translation
        re.UNICODE
    )
    
    # Pattern for example sentences: "English sentence" (Vietnamese translation)
    example_pattern = re.compile(
        r'^["\"](.+?)["\"]'             # "English sentence"
        r'\s*'
        r'[\(\（](.+?)[\)\）]',          # (Vietnamese translation)
        re.UNICODE
    )
    
    current_vocab = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Try to match vocabulary pattern
        vocab_match = vocab_pattern.match(line)
        if vocab_match:
            # Save previous vocab if exists
            if current_vocab:
                results.append(current_vocab)
            
            word = vocab_match.group(1).strip()
            phonetic = vocab_match.group(2).strip()
            translation_part = vocab_match.group(3).strip()
            
            # Extract context from translation if present (text in parentheses)
            context_match = re.search(r'\(([^)]+)\)\s*\.?\s*$', translation_part)
            context = None
            translation = translation_part
            
            if context_match:
                context = context_match.group(1).strip()
                translation = translation_part[:context_match.start()].strip().rstrip('.,')
            
            current_vocab = {
                'word': word,
                'phonetic': phonetic,
                'translation': translation,
                'context': context,
                'example_en': None,
                'example_vi': None
            }
            continue
        
        # Try to match example sentence pattern
        example_match = example_pattern.match(line)
        if example_match and current_vocab:
            current_vocab['example_en'] = example_match.group(1).strip()
            current_vocab['example_vi'] = example_match.group(2).strip()
            continue
    
    # Don't forget the last vocab
    if current_vocab:
        results.append(current_vocab)
    
    return results


def parse_vocabulary_with_examples(text: str) -> List[Dict]:
    """
    Enhanced parser that also captures numbered items and example sentences.
    
    Handles formats like:
    1. Từ khóa:
    Self-invocation /phonetic/: Translation
    
    2. Mẫu câu:
    "English sentence" (Vietnamese translation)
    """
    results = []
    
    # First pass: extract vocabulary with phonetics
    vocab_pattern = re.compile(
        r'([A-Za-z][\w\s\-\']*?)\s*/([^/]+)/\s*[:\-–]\s*([^\n]+)',
        re.UNICODE | re.MULTILINE
    )
    
    for match in vocab_pattern.finditer(text):
        word = match.group(1).strip()
        phonetic = match.group(2).strip()
        translation_raw = match.group(3).strip()
        
        # Clean translation - remove parenthetical context
        context_match = re.search(r'\(([^)]+)\)\s*\.?\s*$', translation_raw)
        context = None
        translation = translation_raw
        
        if context_match:
            context = context_match.group(1).strip()
            translation = translation_raw[:context_match.start()].strip().rstrip('.,')
        
        results.append({
            'word': word,
            'phonetic': phonetic,
            'translation': translation,
            'context': context,
            'example_en': None,
            'example_vi': None
        })
    
    # Second pass: extract example sentences
    example_pattern = re.compile(
        r'["\"]([^"\""]+)["\"]'
        r'\s*'
        r'[\(\（]([^)\）]+)[\)\）]',
        re.UNICODE
    )
    
    examples = []
    for match in example_pattern.finditer(text):
        examples.append({
            'en': match.group(1).strip(),
            'vi': match.group(2).strip()
        })
    
    # Try to associate examples with vocabulary
    # Simple heuristic: if example contains the word, associate it
    for vocab in results:
        word_lower = vocab['word'].lower()
        for ex in examples:
            if word_lower in ex['en'].lower() and not vocab['example_en']:
                vocab['example_en'] = ex['en']
                vocab['example_vi'] = ex['vi']
                break
    
    # If we have standalone examples (not associated with vocab), add them as phrases
    used_examples = {(v['example_en'], v['example_vi']) for v in results if v['example_en']}
    for ex in examples:
        if (ex['en'], ex['vi']) not in used_examples:
            # Add as a phrase entry
            results.append({
                'word': ex['en'],
                'phonetic': None,
                'translation': ex['vi'],
                'context': 'Example sentence',
                'example_en': ex['en'],
                'example_vi': ex['vi']
            })
    
    return results
