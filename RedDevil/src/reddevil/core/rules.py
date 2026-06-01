import itertools
from typing import List, Generator

class RuleEngine:
    """Parses and executes industry-standard Hashcat rules (.rule syntax) and mutations"""
    
    @staticmethod
    def parse_and_apply_rule(rule_line: str, word: str) -> str:
        rule_line = rule_line.strip()
        if not rule_line or rule_line.startswith("#"):
            return word
            
        cmd = rule_line[0]
        try:
            if cmd == ':':  # Nothing/No-op
                return word
            elif cmd == 'u':  # Uppercase all
                return word.upper()
            elif cmd == 'l':  # Lowercase all
                return word.lower()
            elif cmd == 'c':  # Capitalize
                return word.capitalize()
            elif cmd == 'r':  # Reverse string
                return word[::-1]
            elif cmd == 'd':  # Duplicate word
                return word + word
            elif cmd == '$':  # Append character: $x
                return word + rule_line[1]
            elif cmd == '^':  # Prepend character: ^x
                return rule_line[1] + word
        except IndexOutOfBound:
            pass
        return word

    @staticmethod
    def execute_combinator(wordlist_a: List[str], wordlist_b: List[str]) -> Generator[str, None, None]:
        """Creates an optimized Cartesian matrix combining two independent text files"""
        for word_a, word_b in itertools.product(wordlist_a, wordlist_b):
            yield f"{word_a}{word_b}"