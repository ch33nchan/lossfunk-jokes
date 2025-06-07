# jokebot/llm_judge.py
import json
from typing import Dict, Optional, Tuple, List
from.openrouter_client import OpenRouterClient # Corrected import

class LLMJudge:
    def __init__(self, llm_client: OpenRouterClient):
        self.llm_client = llm_client
        self.transparency_data = {"evaluations":}


    def get_joke_evaluation_rubric(self) -> str: # [6, 7, 8]
        return """
        Please evaluate the joke based on the following criteria. Provide a score from 1 (very poor) to 10 (excellent) for each, and an overall funniness score (1-10). Also, provide a brief overall rationale.

        1.  **Originality/Novelty:** (1-10) Does the joke feel fresh and not like a common or overused joke?
        2.  **Coherence/Understandability:** (1-10) Is the joke easy to understand and logically sound (within its comedic frame)?
        3.  **Setup Effectiveness:** (1-10) Does the setup effectively build anticipation or misdirection?
        4.  **Punchline Impact:** (1-10) Is the punchline surprising, witty, and satisfying?
        5.  **Brevity/Conciseness:** (1-10) Is the joke concise, or does it have unnecessary words? (Note: Brevity is often good, but not always. Judge in context.)
        6.  **Overall Funniness:** (1-10) How funny is the joke overall?

        Output your evaluation in JSON format like this:
        {
            "originality": <score_1_10>,
            "coherence": <score_1_10>,
            "setup_effectiveness": <score_1_10>,
            "punchline_impact": <score_1_10>,
            "brevity": <score_1_10>,
            "overall_funniness": <score_1_10>,
            "rationale": "<brief overall textual rationale for the funniness score>"
        }
        """

    def _construct_judge_prompt(self, joke_text: str, rubric: str, bias_instructions: Optional[str] = None) -> str:
        bias_mitigation_text = bias_instructions or (
            "IMPORTANT: Evaluate objectively. Do not let the length of the joke unduly influence your funniness score. "
            "A short joke can be funnier than a long one. Focus on cleverness and impact. "
            "The order of presentation should not affect your judgment if multiple jokes were being compared (though here you evaluate one)."
        ) # [9, 10, 11, 6, 12, 13]

        return (
            f"You are a discerning comedy critic. Your task is to evaluate the following joke based on the provided rubric. "
            f"Please be thoughtful and analytical in your assessment.\n\n"
            f"Joke to Evaluate:\n\"\"\"\n{joke_text}\n\"\"\"\n\n"
            f"Evaluation Rubric and Output Format:\n{rubric}\n\n"
            f"{bias_mitigation_text}\n\n"
            f"Provide your evaluation in the specified JSON format only."
        )

    def evaluate_joke(self,
                      joke_text: str,
                      judge_model_name: str,
                      bias_instructions: Optional[str] = None) -> Optional]:
        rubric = self.get_joke_evaluation_rubric()
        prompt_content = self._construct_judge_prompt(joke_text, rubric, bias_instructions)
        
        messages = [{"role": "user", "content": prompt_content}]
        response_format_json = {"type": "json_object"} # [3]
        
        raw_response = self.llm_client.get_completion(
            judge_model_name, 
            messages, 
            temperature=0.3, 
            max_tokens=400,
            response_format=response_format_json
        )

        evaluation = None
        if raw_response:
            try:
                evaluation = json.loads(raw_response)
                required_keys = {"originality", "coherence", "setup_effectiveness", "punchline_impact", "brevity", "overall_funniness", "rationale"}
                if not required_keys.issubset(evaluation.keys()):
                    print(f"LLM Judge response missing required keys: {raw_response}")
                    evaluation = None 
            except json.JSONDecodeError:
                print(f"LLM Judge response was not valid JSON: {raw_response}")
                evaluation = None
        
        self.transparency_data["evaluations"].append({
            "joke_text": joke_text, "judge_model": judge_model_name, "raw_response": raw_response, "parsed_evaluation": evaluation
        })
        return evaluation

    def get_transparency_data(self) -> Dict:
        return self.transparency_data