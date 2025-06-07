
import re
from typing import Optional, List, Dict, Any
from nltk.util import ngrams
from nltk.tokenize import word_tokenize
from.openrouter_client import OpenRouterClient # Corrected import


try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None
    print("Warning: duckduckgo-search library not found. Web cross-referencing will be skipped. Run 'pip install duckduckgo-search'")


class NoveltyChecker:
    def __init__(self, llm_client: OpenRouterClient, joke_corpus_path: Optional[str] = None): # joke_corpus_path is now unused but kept for signature consistency if ever needed
        self.llm_client = llm_client
        self.known_jokes_corpus: List[str] = # No longer loading from file
        self.transparency_data = {"novelty_checks":}

       

    def _preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def check_n_gram_overlap(self, joke_text: str, n: int = 7) -> float:
        """
        N-gram overlap is no longer used as we don't have a local corpus.
        Returns 0.0 to indicate no overlap found with a (non-existent) local corpus.
        [14, 15, 16, 17]
        """
        # This method is effectively disabled without a local corpus.
        # Returning 0.0 means it's considered "novel" by this specific check.
        return 0.0 

    def check_semantic_similarity_with_corpus(self, joke_text: str, embedding_model_name: Optional[str] = None) -> float:
        """
        Semantic similarity with a local corpus is no longer used.
        Returns 0.0 to indicate no similarity found with a (non-existent) local corpus.
        [18, 19, 20, 21, 22]
        """
        # This method is effectively disabled without a local corpus.
        # Returning 0.0 means it's considered "novel" by this specific check.
        return 0.0

    def check_web_cross_reference(self, joke_text: str, max_results: int = 5) -> float:
        """
        Checks if the joke is widely found online using DuckDuckGo.
        Returns a penalty score: 0.0 if not found or few results, up to 1.0 if widely found.
        Higher score = LESS novel (more widely found).
        [23, 24]
        """
        if DDGS is None:
            print("Web cross-referencing skipped: duckduckgo-search library not available.")
            return 0.0 # Assume novel if search can't be performed

        try:
            # Search for the punchline or a significant part of the joke
            # A simple heuristic: take the last 10 words as a query, or the whole joke if short
            query_words = joke_text.split()
            if len(query_words) > 10:
                query = " ".join(query_words[-10:])
            else:
                query = joke_text
            
            # Using DDGS context manager for safety
            with DDGS() as ddgs:
                results = list(ddgs.text(f'"{query}"', max_results=max_results)) # Exact phrase search
            
            # print(f"Web search for '{query}' found {len(results)} results.")
            
            if not results:
                return 0.0 # Not found, high novelty
            
            # Simple scoring: more results = less novel
            # This is a basic heuristic and can be refined
            if len(results) >= 3: # Found on multiple sites
                return 1.0 # High penalty (widely found)
            elif len(results) >= 1: # Found on at least one site
                return 0.5 # Medium penalty
            return 0.0 # Low penalty (few/no distinct results)

        except Exception as e:
            print(f"Error during web search cross-referencing: {e}")
            return 0.2 # Default to a small penalty if search fails, to be conservative
    
    def assess_perceived_novelty_with_llm(self, joke_text: str, judge_model_name: str) -> float:
        """
        Uses an LLM to give a subjective score for perceived novelty.
        Returns a score from 0.0 (not novel) to 1.0 (very novel).
        [25, 26, 27, 28, 19, 29]
        """
        prompt_content = (
            f"Please evaluate the following joke for its perceived novelty and originality. "
            f"Does it feel like a fresh, creative joke, or does it seem like a common, recycled, or clichéd joke?\n\n"
            f"Joke: \"{joke_text}\"\n\n"
            f"Provide a novelty score from 0.0 (very unoriginal, common) to 1.0 (highly original, fresh). "
            f"Output only the numerical score. For example: 0.7"
        )
        messages = [{"role": "user", "content": prompt_content}]
        response = self.llm_client.get_completion(judge_model_name, messages, temperature=0.3, max_tokens=10)
        if response:
            try:
                score = float(response.strip())
                return max(0.0, min(1.0, score))
            except ValueError:
                print(f"Could not parse novelty score from LLM: {response}")
        return 0.5 

    def calculate_overall_novelty_score(self, joke_text: str, 
                                        perceived_novelty_model_name: Optional[str] = None) -> Dict[str, float]:
        """
        Calculates a composite novelty score, relying on web search and LLM perception.
        [30, 31, 25, 19]
        """
        scores = {
            "n_gram_overlap_score": 0.0, # Unused
            "semantic_similarity_corpus_score": 0.0, # Unused
            "web_found_penalty_score": 0.0, # Higher = less novel (more found online)
            "perceived_novelty_llm_score": 0.5, # Higher = more novel
            "final_novelty_score": 0.5 # Higher = more novel
        }

        # N-gram and semantic similarity with local corpus are now disabled
        scores["n_gram_overlap_score"] = self.check_n_gram_overlap(joke_text) # Will be 0.0
        scores["semantic_similarity_corpus_score"] = self.check_semantic_similarity_with_corpus(joke_text) # Will be 0.0
        
        scores["web_found_penalty_score"] = self.check_web_cross_reference(joke_text)
        
        if perceived_novelty_model_name:
            scores["perceived_novelty_llm_score"] = self.assess_perceived_novelty_with_llm(joke_text, perceived_novelty_model_name)

        # Combine scores:
        # Start with LLM's perceived novelty.
        # Penalize heavily if found on the web.
        # N-gram and semantic (corpus) scores will be 0, so they won't affect the calculation.
        
        novelty_score = scores["perceived_novelty_llm_score"]
        novelty_score -= scores["web_found_penalty_score"] * 0.7 # Strong penalty if widely found online
        # The other scores (n_gram_overlap_score, semantic_similarity_corpus_score) are 0.0
        # so their weighted subtraction won't change novelty_score here.

        scores["final_novelty_score"] = max(0.0, min(1.0, novelty_score))
        
        self.transparency_data["novelty_checks"].append({
            "joke_text": joke_text, "scores": scores.copy()
        })
        return scores

    def get_transparency_data(self) -> Dict:
        return self.transparency_data