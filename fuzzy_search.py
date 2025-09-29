import keyboard
import os
import sys
from icecream import ic

def levenshtein(a: str, b: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if a == b:
        return 0
    if len(a) == 0:
        return len(b)
    if len(b) == 0:
        return len(a)

    # Ensure a is the shorter for a tiny memory win (optional).
    if len(a) > len(b):
        a, b = b, a

    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        current = [i]
        for j, cb in enumerate(b, start=1):
            ins = current[j - 1] + 1       # insertion
            dele = previous[j] + 1         # deletion
            subst = previous[j - 1] + (ca != cb)  # substitution
            current.append(min(ins, dele, subst))
        previous = current
    return previous[-1]

def load_words(path: str ="words.txt", case_sensitive: bool = False) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        words = []
        for line in f:
            w = line.strip()
            if not case_sensitive:
                w = w.lower()
            if w:
                words.append(w)
        return words

def fuzzy_search(query: str, words: list[str], top_k: int = 5, max_dist: int | None = None, case_sensitive: bool = False) -> list[str]:
    """
    Return top fuzzy matches for `query` from `words`.
    
    Parameters:
        query: The partial word to match.
        words: List of candidate words.
        top_k: Maximum number of results to return.
        max_dist: Maximum allowed Levenshtein distance.
        case_sensitive: Whether matching is case sensitive.
    
    Returns:
        List of formatted strings showing word, distance, and similarity.
    """
    if not case_sensitive:
        query = query.lower()
        words = [w.lower() for w in words]

    # Compute distances
    results = []
    for w in words:
        d = levenshtein(query, w)
        if max_dist is None or d <= max_dist:
            results.append((d, w))

    # Sort by distance then alphabetically
    results.sort(key=lambda x: (x[0], x[1]))

    # Format results
    formatted = []
    for d, w in results[:top_k]:
        max_len = max(len(query), len(w))
        sim = 1.0 - (d / max_len) if max_len else 1.0
        formatted.append(f"{w}  (distance={d}, similarity={sim:.2f})")

    if query == "":
        return []
    else:
        return formatted

def print_fuzzy_results(results: list[str], query: str = ""):
    """
    Pretty-print fuzzy search results sorted by similarity, highlighting typed query.
    
    Each result string should be in the format:
        "word  (distance=d, similarity=s)"
    """
    if not results:
        return

    parsed = []
    for r in results:
        word_part = r.split("  (")[0]
        dist_part = r[r.find("distance=")+9 : r.find(", similarity")]
        sim_part = r[r.find("similarity=")+11 : r.find(")")]
        parsed.append((word_part, float(sim_part), int(dist_part)))

    # Sort by similarity descending, then by word alphabetically
    parsed.sort(key=lambda x: (-x[1], x[0]))

    # Determine padding
    max_word_len = max(len(word) for word, _, _ in parsed)

    for word, sim, dist in parsed:
        percent = int(sim * 100)

        # Highlight matching part of the word
        highlight_len = len(query)
        word_lower = word.lower()
        query_lower = query.lower()
        if word_lower.startswith(query_lower) and highlight_len > 0:
            highlighted = f"\033[92m{word[:highlight_len].title()}\033[0m{word[highlight_len:].title()}"
        else:
            highlighted = word.title()

        # Dots and spacing
        dots = "." * (max_word_len + 15 - len(word))
        dist_offset = "" if percent == 100 else " " if percent != 0 else "  "

        print(f"{highlighted}{dots}{percent}% {dist_offset}({dist})")



print("Press ESC to quit.")

words = load_words("words.txt", False)
word = ""

while True:
        event = keyboard.read_event(suppress=True)  # Read keyboard input
        if event.event_type == "down":  # Only process key down events
            char = event.name
            if char == "space": 
                word += " "
            elif char == "backspace":
                 word = word[:-1]
            elif char == "esc":
                sys.exit()
            elif len(char) > 1:  # Ignore special keys like Shift, Ctrl, etc.
                continue
            else:
                word += char
            
            
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Press ESC to quit.\n")
            ic(word)
            print()
            results = fuzzy_search(word, words, 10, 4, False)
            print_fuzzy_results(results, word)

