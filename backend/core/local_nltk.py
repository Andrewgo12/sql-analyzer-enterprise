"""
Local NLTK Implementation
Basic replacement for NLTK functionality used in SQL Analyzer.
This ensures the application works without external NLTK dependency.
"""

import re
from typing import List, Set, Dict, Optional
from collections import defaultdict


# Common English stop words
ENGLISH_STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours',
    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers',
    'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves',
    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does',
    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
    'while', 'of', 'at', 'by', 'for', 'with', 'through', 'during', 'before', 'after',
    'above', 'below', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
    'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will',
    'just', 'don', 'should', 'now'
}


def word_tokenize(text: str) -> List[str]:
    """
    Tokenize text into words.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of word tokens
    """
    if not text:
        return []
    
    # Simple word tokenization using regex
    # This pattern matches sequences of word characters
    pattern = r'\b\w+\b'
    tokens = re.findall(pattern, text.lower())
    
    return tokens


def sent_tokenize(text: str) -> List[str]:
    """
    Tokenize text into sentences.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of sentence tokens
    """
    if not text:
        return []
    
    # Simple sentence tokenization using regex
    # This pattern splits on sentence-ending punctuation
    pattern = r'[.!?]+\s+'
    sentences = re.split(pattern, text.strip())
    
    # Remove empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    
    return sentences


class WordNetLemmatizer:
    """
    Simple lemmatizer that handles basic word forms.
    """
    
    def __init__(self):
        # Basic lemmatization rules
        self.plural_rules = [
            (r'ies$', 'y'),
            (r'ves$', 'f'),
            (r'oes$', 'o'),
            (r'ses$', 's'),
            (r'ches$', 'ch'),
            (r'shes$', 'sh'),
            (r'xes$', 'x'),
            (r'zes$', 'z'),
            (r's$', ''),
        ]
        
        self.verb_rules = [
            (r'ing$', ''),
            (r'ed$', ''),
            (r'er$', ''),
            (r'est$', ''),
        ]
    
    def lemmatize(self, word: str, pos: str = 'n') -> str:
        """
        Lemmatize a word.
        
        Args:
            word: Word to lemmatize
            pos: Part of speech ('n' for noun, 'v' for verb, 'a' for adjective)
            
        Returns:
            Lemmatized word
        """
        if not word:
            return word
        
        word = word.lower()
        
        if pos == 'n':  # Noun
            for pattern, replacement in self.plural_rules:
                if re.search(pattern, word):
                    return re.sub(pattern, replacement, word)
        
        elif pos == 'v':  # Verb
            for pattern, replacement in self.verb_rules:
                if re.search(pattern, word):
                    result = re.sub(pattern, replacement, word)
                    # Avoid empty results
                    if result:
                        return result
        
        return word


class StopWords:
    """
    Stop words handler.
    """
    
    def __init__(self):
        self.words = {
            'english': ENGLISH_STOP_WORDS
        }
    
    def words(self, language: str = 'english') -> Set[str]:
        """Get stop words for a language."""
        return self.words.get(language, set())


class WordNet:
    """
    Simple WordNet-like functionality.
    """
    
    # Basic synonym groups for common words
    SYNSETS = {
        'user': ['user', 'person', 'individual', 'account', 'member'],
        'customer': ['customer', 'client', 'buyer', 'patron'],
        'product': ['product', 'item', 'goods', 'merchandise'],
        'order': ['order', 'purchase', 'transaction', 'request'],
        'payment': ['payment', 'transaction', 'billing', 'charge'],
        'address': ['address', 'location', 'place', 'residence'],
        'phone': ['phone', 'telephone', 'mobile', 'contact'],
        'email': ['email', 'mail', 'message', 'contact'],
        'date': ['date', 'time', 'timestamp', 'when'],
        'name': ['name', 'title', 'label', 'identifier'],
        'id': ['id', 'identifier', 'key', 'number'],
        'status': ['status', 'state', 'condition', 'flag'],
        'type': ['type', 'kind', 'category', 'class'],
        'description': ['description', 'details', 'info', 'text'],
        'price': ['price', 'cost', 'amount', 'value'],
        'quantity': ['quantity', 'amount', 'count', 'number'],
    }
    
    @classmethod
    def synsets(cls, word: str) -> List[str]:
        """
        Get synsets (synonym sets) for a word.
        
        Args:
            word: Word to find synsets for
            
        Returns:
            List of related words
        """
        word = word.lower()
        
        # Direct lookup
        if word in cls.SYNSETS:
            return cls.SYNSETS[word]
        
        # Search in values
        for key, synonyms in cls.SYNSETS.items():
            if word in synonyms:
                return synonyms
        
        return [word]  # Return the word itself if no synsets found


# Create module-like objects for compatibility
class Corpus:
    """Corpus access."""
    
    def __init__(self):
        self.stopwords = StopWords()


class Tokenize:
    """Tokenization functions."""
    
    @staticmethod
    @staticmethod
class Stem:
    """Stemming functions."""
    
    def __init__(self):
        self.WordNetLemmatizer = WordNetLemmatizer


# Create NLTK-compatible module structure
class NLTK:
    """Main NLTK-compatible class."""
    
    def __init__(self):
        self.corpus = Corpus()
        self.tokenize = Tokenize()
        self.stem = Stem()
        self.wordnet = WordNet()
    
    def download(self, resource: str, quiet: bool = True):
        """Mock download function - does nothing since we have local data."""
        pass


# Create module-level instance
nltk = NLTK()

# Module-level functions for direct import compatibility
def download(resource: str, quiet: bool = True):
    """Mock download function."""
    pass


# Create submodules for import compatibility
class CorpusModule:
    stopwords = StopWords()


class TokenizeModule:
    word_tokenize = word_tokenize
    sent_tokenize = sent_tokenize


class StemModule:
    WordNetLemmatizer = WordNetLemmatizer


class WordNetModule:
    synsets = WordNet.synsets


# Make submodules available
corpus = CorpusModule()
tokenize = TokenizeModule()
stem = StemModule()
wordnet = WordNetModule()
