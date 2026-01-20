import re

class TopicService:
    @staticmethod
    def extract_topics(text: str) -> list[str]:
        """
        Extracts high-level topics/headers using hierarchical heuristics (Regex).
        Priority: H1 > H2 > H3. Returns the highest level found.
        """
        lines = text.split('\n')
        
        # Clean lines & Normalize spaces
        cleaned_lines = []
        for line in lines:
            norm_line = " ".join(line.split()) 
            if norm_line and len(norm_line) < 150:
                cleaned_lines.append(norm_line)
                
        # Regex Priorities
        h1_regex = re.compile(r'^(?:(?:\d+\.)|[IVX]+\.?|Chapter\s+\d+|Capítulo\s+\d+|Módulo\s+\d+)\s+([A-Z].{2,})', re.IGNORECASE)
        h2_regex = re.compile(r'^(?:(?:\d+\.\d+\.?)|[A-Z]\))\s+([A-Z].{2,})', re.IGNORECASE)
        h3_regex = re.compile(r'^(?:(?:\d+\.\d+\.\d+\.?)|[a-z]\))\s+([A-Z].{2,})', re.IGNORECASE)
        loose_regex = re.compile(r'^(?![•●-])([A-ZÀ-Ú][^.!?]{3,120})$') 

        found_h1 = []
        found_h2 = []
        found_h3 = []
        found_loose = []

        for line in cleaned_lines:
            if h1_regex.match(line):
                found_h1.append(line)
                continue 
            if h2_regex.match(line):
                found_h2.append(line)
                continue
            if h3_regex.match(line):
                found_h3.append(line)
                continue
            if loose_regex.match(line) and "página" not in line.lower() and "page" not in line.lower():
                found_loose.append(line)

        def dedup(lst):
            seen = set()
            out = []
            for x in lst:
                if x not in seen:
                    out.append(x)
                    seen.add(x)
            return out

        if found_h1: return dedup(found_h1)[:20]
        if found_h2: return dedup(found_h2)[:20]
        if found_h3: return dedup(found_h3)[:20]
        if found_loose: return dedup(found_loose)[:25]

        return ["Tópicos Gerais"]
