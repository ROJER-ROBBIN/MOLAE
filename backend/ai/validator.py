import re

class ResponseValidator:
    def __init__(self):
        # Triggers that might indicate a fabricated memory
        self.claim_triggers = [
            r"i remember",
            r"we went",
            r"you told me",
            r"we did",
            r"last week",
            r"that day",
            r"do you remember",
            r"when we"
        ]
        self.claim_pattern = re.compile("|".join(self.claim_triggers), re.IGNORECASE)

    def validate_response(self, response_text, retrieved_memories):
        """
        Check if the response text makes a claim that is unsupported by the retrieved memories.
        If a claim trigger is found, we do a basic check to see if the keywords of the response 
        are present in the historical memories.
        
        Returns (is_valid, fallback_response_if_invalid)
        """
        if not self.claim_pattern.search(response_text):
            return True, None
            
        # If there's a claim, check if we have retrieved memories to back it up.
        if not retrieved_memories:
            return False, "I don't have a saved memory of that."
            
        # Combine all memory text
        all_memory_text = " ".join([m.get("document", "").lower() for m in retrieved_memories])
        
        # Check if substantive words from the response are in the memories.
        # This is a simple heuristic for Phase 6.
        words = re.findall(r'\b\w+\b', response_text.lower())
        stop_words = {"i", "you", "we", "the", "a", "an", "is", "was", "are", "were", "to", "and", "of", "in", "for"}
        substantive_words = [w for w in words if w not in stop_words and len(w) > 3]
        
        if not substantive_words:
            return True, None # Not enough substantive words to invalidate
            
        # If less than 20% of the substantive words in the response appear in the memory text, 
        # it might be fabricating.
        matches = sum(1 for w in substantive_words if w in all_memory_text)
        match_ratio = matches / len(substantive_words)
        
        if match_ratio < 0.2:
            return False, "I don't have a saved memory of that."
            
        return True, None
