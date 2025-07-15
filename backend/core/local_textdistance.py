"""
Local Text Distance Implementation
Complete replacement for textdistance library used in SQL Analyzer.
This ensures the application works without external textdistance dependency.
"""

from typing import Union, Sequence
import re


def levenshtein(s1: Union[str, Sequence], s2: Union[str, Sequence]) -> int:
    """
    Calculate Levenshtein distance between two strings or sequences.
    
    The Levenshtein distance is the minimum number of single-character edits
    (insertions, deletions, or substitutions) required to change one string
    into another.
    
    Args:
        s1: First string or sequence
        s2: Second string or sequence
        
    Returns:
        Levenshtein distance as integer
    """
    if s1 == s2:
        return 0
    
    len1, len2 = len(s1), len(s2)
    
    # Handle empty strings
    if len1 == 0:
        return len2
    if len2 == 0:
        return len1
    
    # Create matrix
    matrix = [[0] * (len2 + 1) for _ in range(len1 + 1)]
    
    # Initialize first row and column
    for i in range(len1 + 1):
        matrix[i][0] = i
    for j in range(len2 + 1):
        matrix[0][j] = j
    
    # Fill matrix
    for i in range(1, len1 + 1):
        for j in range(1, len2 + 1):
            if s1[i-1] == s2[j-1]:
                cost = 0
            else:
                cost = 1
            
            matrix[i][j] = min(
                matrix[i-1][j] + 1,      # deletion
                matrix[i][j-1] + 1,      # insertion
                matrix[i-1][j-1] + cost  # substitution
            )
    
    return matrix[len1][len2]


def hamming(s1: Union[str, Sequence], s2: Union[str, Sequence]) -> int:
    """
    Calculate Hamming distance between two strings or sequences.
    
    The Hamming distance is the number of positions at which the
    corresponding symbols are different.
    
    Args:
        s1: First string or sequence
        s2: Second string or sequence
        
    Returns:
        Hamming distance as integer
        
    Raises:
        ValueError: If strings have different lengths
    """
    if len(s1) != len(s2):
        raise ValueError("Strings must have the same length for Hamming distance")
    
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def jaro(s1: str, s2: str) -> float:
    """
    Calculate Jaro similarity between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Jaro similarity as float between 0 and 1
    """
    if s1 == s2:
        return 1.0
    
    len1, len2 = len(s1), len(s2)
    
    if len1 == 0 or len2 == 0:
        return 0.0
    
    # Calculate matching window
    match_window = max(len1, len2) // 2 - 1
    if match_window < 0:
        match_window = 0
    
    # Initialize match arrays
    s1_matches = [False] * len1
    s2_matches = [False] * len2
    
    matches = 0
    transpositions = 0
    
    # Find matches
    for i in range(len1):
        start = max(0, i - match_window)
        end = min(i + match_window + 1, len2)
        
        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = s2_matches[j] = True
            matches += 1
            break
    
    if matches == 0:
        return 0.0
    
    # Count transpositions
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1
    
    return (matches / len1 + matches / len2 + (matches - transpositions / 2) / matches) / 3


def jaro_winkler(s1: str, s2: str, prefix_scale: float = 0.1) -> float:
    """
    Calculate Jaro-Winkler similarity between two strings.
    
    Args:
        s1: First string
        s2: Second string
        prefix_scale: Scaling factor for common prefix (default 0.1)
        
    Returns:
        Jaro-Winkler similarity as float between 0 and 1
    """
    jaro_sim = jaro(s1, s2)
    
    if jaro_sim < 0.7:
        return jaro_sim
    
    # Calculate common prefix length (up to 4 characters)
    prefix_len = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break
    
    return jaro_sim + (prefix_len * prefix_scale * (1 - jaro_sim))


def jaccard(s1: Union[str, set], s2: Union[str, set]) -> float:
    """
    Calculate Jaccard similarity between two strings or sets.
    
    Args:
        s1: First string or set
        s2: Second string or set
        
    Returns:
        Jaccard similarity as float between 0 and 1
    """
    if isinstance(s1, str):
        s1 = set(s1)
    if isinstance(s2, str):
        s2 = set(s2)
    
    intersection = len(s1.intersection(s2))
    union = len(s1.union(s2))
    
    if union == 0:
        return 1.0 if len(s1) == len(s2) == 0 else 0.0
    
    return intersection / union


def cosine(s1: str, s2: str) -> float:
    """
    Calculate cosine similarity between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Cosine similarity as float between 0 and 1
    """
    # Create character frequency vectors
    chars1 = {}
    chars2 = {}
    
    for char in s1:
        chars1[char] = chars1.get(char, 0) + 1
    
    for char in s2:
        chars2[char] = chars2.get(char, 0) + 1
    
    # Get all unique characters
    all_chars = set(chars1.keys()) | set(chars2.keys())
    
    if not all_chars:
        return 1.0
    
    # Calculate dot product and magnitudes
    dot_product = 0
    magnitude1 = 0
    magnitude2 = 0
    
    for char in all_chars:
        freq1 = chars1.get(char, 0)
        freq2 = chars2.get(char, 0)
        
        dot_product += freq1 * freq2
        magnitude1 += freq1 * freq1
        magnitude2 += freq2 * freq2
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 ** 0.5 * magnitude2 ** 0.5)


def normalized_levenshtein(s1: str, s2: str) -> float:
    """
    Calculate normalized Levenshtein distance (0-1 scale).
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Normalized distance as float between 0 and 1
    """
    max_len = max(len(s1), len(s2))
    if max_len == 0:
        return 0.0
    
    return levenshtein(s1, s2) / max_len


def similarity(s1: str, s2: str, method: str = 'levenshtein') -> float:
    """
    Calculate similarity between two strings using specified method.
    
    Args:
        s1: First string
        s2: Second string
        method: Similarity method ('levenshtein', 'jaro', 'jaro_winkler', 'jaccard', 'cosine')
        
    Returns:
        Similarity score as float
    """
    method = method.lower()
    
    if method == 'levenshtein':
        return 1.0 - normalized_levenshtein(s1, s2)
    elif method == 'jaro':
        return jaro(s1, s2)
    elif method == 'jaro_winkler':
        return jaro_winkler(s1, s2)
    elif method == 'jaccard':
        return jaccard(s1, s2)
    elif method == 'cosine':
        return cosine(s1, s2)
    else:
        raise ValueError(f"Unknown similarity method: {method}")


def distance(s1: str, s2: str, method: str = 'levenshtein') -> Union[int, float]:
    """
    Calculate distance between two strings using specified method.
    
    Args:
        s1: First string
        s2: Second string
        method: Distance method ('levenshtein', 'hamming', 'jaccard', 'cosine')
        
    Returns:
        Distance score
    """
    method = method.lower()
    
    if method == 'levenshtein':
        return levenshtein(s1, s2)
    elif method == 'hamming':
        return hamming(s1, s2)
    elif method == 'jaccard':
        return 1.0 - jaccard(s1, s2)
    elif method == 'cosine':
        return 1.0 - cosine(s1, s2)
    else:
        raise ValueError(f"Unknown distance method: {method}")


# Create a module-like object that matches textdistance API
class TextDistance:
    """Main textdistance-compatible class."""
    
    @staticmethod
    def levenshtein(s1, s2):
        return levenshtein(s1, s2)
    
    @staticmethod
    def hamming(s1, s2):
        return hamming(s1, s2)
    
    @staticmethod
    def jaro(s1, s2):
        return jaro(s1, s2)
    
    @staticmethod
    def jaro_winkler(s1, s2):
        return jaro_winkler(s1, s2)
    
    @staticmethod
    def jaccard(s1, s2):
        return jaccard(s1, s2)
    
    @staticmethod
    def cosine(s1, s2):
        return cosine(s1, s2)


# Create module-level instance for compatibility
textdistance = TextDistance()
