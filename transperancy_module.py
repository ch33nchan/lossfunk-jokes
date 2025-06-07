# jokebot/transparency_module.py
from typing import Dict, List, Any, Optional

class TransparencyProvider:
    def get_plansearch_code_details(self) -> Dict]]:
        # These are static descriptions of the code's intent
        return {
            "plansearch_for_jokes.py": [
                {
                    "function_name": "_prompt_for_observations",
                    "description": "Generates first-order (from topic) or second-order (from existing observations) comedic insights. Crucial for seeding the idea space. [5]",
                    "code_snippet": """
def _prompt_for_observations(self, topic: str, model_name: str, existing_observations: Optional[List[str]] = None) -> List[str]:
    #... (prompt construction based on whether existing_observations are provided)
    messages = [{"role": "user", "content": prompt_content}]
    response = self.llm_client.get_completion(model_name, messages, temperature=0.8)
    #... (parsing logic)...
    return parsed_observations
"""
                },
                {
                    "function_name": "_generate_observation_combinations",
                    "description": "Systematically creates subsets of observations (e.g., pairs) to explore combined comedic angles, a core PLANSEARCH diversity technique. [5]",
                    "code_snippet": """
def _generate_observation_combinations(self, observations: List[str], max_subset_size: int = 2) -> List]:
    #... (uses itertools.combinations)...
    return combinations
"""
                },
                {
                    "function_name": "_prompt_for_joke_plan",
                    "description": "Takes a combination of observations and asks an LLM to formulate a high-level strategy or structure for a joke. [5]",
                    "code_snippet": """
def _prompt_for_joke_plan(self, topic: str, observation_combo: Tuple[str,...], model_name: str) -> Optional[str]:
    #... (constructs prompt with topic and observation_combo)...
    plan = self.llm_client.get_completion(model_name, messages, temperature=0.7)
    return plan
"""
                },
                 {
                    "function_name": "_prompt_for_critique",
                    "description": "Implements the 'Your idea is wrong' refinement step from PLANSEARCH [5] by asking an LLM to critique a generated joke against its plan, fostering diversity.",
                    "code_snippet": """
def _prompt_for_critique(self, joke: str, plan: str, model_name: str) -> Optional[str]:
    #... (constructs prompt with plan and joke for critique)...
    critique = self.llm_client.get_completion(model_name, messages, temperature=0.6)
    return critique
"""
                }
            ],
            "llm_judge.py": [
                {
                    "function_name": "evaluate_joke",
                    "description": "Uses a judge LLM to evaluate a joke based on a predefined rubric, incorporating bias mitigation instructions. [9, 32, 10, 11, 6, 12, 33, 34, 35, 36, 13, 37, 7]",
                    "code_snippet": """
def evaluate_joke(self, joke_text: str, judge_model_name: str,...) -> Optional]:
    rubric = self.get_joke_evaluation_rubric()
    prompt_content = self._construct_judge_prompt(joke_text, rubric, bias_instructions)
    #... (LLM call with response_format={'type': 'json_object'})...
    #... (JSON parsing and validation)...
    return evaluation
"""
                }
            ],
            "novelty_checker.py":",
                    "code_snippet": """
def check_web_cross_reference(self, joke_text: str, max_results: int = 5) -> float:
    if DDGS is None: return 0.0
    #... (constructs search query from joke_text)...
    with DDGS() as ddgs:
        results = list(ddgs.text(f'"{query}"', max_results=max_results))
    #... (scores based on number of results)...
    return penalty_score
"""
                },
                {
                    "function_name": "assess_perceived_novelty_with_llm",
                    "description": "Asks an LLM to provide a subjective score (0-1) on how novel or fresh a joke feels. [25, 26, 27, 28, 19, 29]",
                    "code_snippet": """
def assess_perceived_novelty_with_llm(self, joke_text: str, judge_model_name: str) -> float:
    #... (constructs prompt asking for novelty score 0.0-1.0)...
    response = self.llm_client.get_completion(judge_model_name, messages, temperature=0.3)
    #... (parses float from response)...
    return score
"""
                }
            ]
        }

    def get_pipeline_visualization_data(self, last_run_data: Optional = None) -> Dict[str, Any]:
        # This creates a generic pipeline structure.
        # `last_run_data` can be used to annotate it with specifics from the actual run.
        
        nodes =", "type": "process_group"},
            {"id": "obs1", "label": "1. First-Order Observations", "type": "process", "parent": "plansearch_group"},
            {"id": "obs2", "label": "2. Second-Order Observations", "type": "process", "parent": "plansearch_group"},
            {"id": "plan_form", "label": "3. Joke Plan Formulation", "type": "process", "parent": "plansearch_group"},
            {"id": "joke_inst", "label": "4. Joke Instantiation & Refinement", "type": "process", "parent": "plansearch_group"},
            {"id": "candidates_out", "label": "Candidate Jokes", "type": "data"},
            
            {"id": "novelty_group", "label": "Novelty Checker Module", "type": "process_group"},
            {"id": "web_check", "label": "Web Cross-Reference [23, 24]", "type": "process", "parent": "novelty_group"},
            {"id": "llm_novelty_perc", "label": "LLM Perceived Novelty [25, 19]", "type": "process", "parent": "novelty_group"},
            {"id": "novelty_scores", "label": "Novelty Scores", "type": "data"},

            {"id": "judge_group", "label": "LLM Judge Module [9, 32, 10, 11, 6, 12, 33, 34, 35, 36, 13, 37, 7]", "type": "process_group"},
            {"id": "funniness_eval", "label": "Funniness Evaluation (Rubric-based, Bias Mitigation)", "type": "process", "parent": "judge_group"},
            {"id": "funniness_scores", "label": "Funniness Scores", "type": "data"},

            {"id": "ranking", "label": "Ranking (Combined Score)", "type": "process"},
            {"id": "final_jokes_display", "label": "Top Jokes Output", "type": "output"}
        ]

        edges = [
            {"from": "start", "to": "obs1"},
            {"from": "obs1", "to": "obs2"},
            {"from": "obs2", "to": "plan_form"},
            {"from": "plan_form", "to": "joke_inst"},
            {"from": "joke_inst", "to": "candidates_out"},
            {"from": "candidates_out", "to": "web_check"},
            {"from": "candidates_out", "to": "llm_novelty_perc"},
            {"from": "web_check", "to": "novelty_scores"},
            {"from": "llm_novelty_perc", "to": "novelty_scores"},
            {"from": "candidates_out", "to": "funniness_eval"},
            {"from": "funniness_eval", "to": "funniness_scores"},
            {"from": "novelty_scores", "to": "ranking"},
            {"from": "funniness_scores", "to": "ranking"},
            {"from": "ranking", "to": "final_jokes_display"}
        ]
        
        annotations = {
            "plansearch_group": "Tackles joke diversity by exploring a natural language 'idea space' before generation. Uses combinatorial observation sampling and critique-refinement. [5]",
            "novelty_group": "Addresses originality by checking joke prevalence on the web and using LLM perception of novelty. Local corpus checks are disabled in this version.",
            "judge_group": "Handles subjective funniness evaluation using a structured rubric and an LLM. Includes prompt-based bias mitigation for verbosity and positional effects. [9, 10, 11, 6, 12, 13]"
        }
        
        # You can augment nodes with data from last_run_data if available
        # For example, show how many observations/plans were actually generated.
        if last_run_data and last_run_data.get('plansearch_data'):
            ps_data = last_run_data['plansearch_data']
            num_obs = len(ps_data.get('observations',))
            num_plans = len(ps_data.get('plans',))
            num_jokes_gen = len(ps_data.get('jokes_generated',))
            for node in nodes:
                if node['id'] == 'obs1':
                    node['label'] += f" (Actual: {num_obs} sets)"
                if node['id'] == 'plan_form':
                    node['label'] += f" (Actual: {num_plans} plans)"
                if node['id'] == 'joke_inst':
                     node['label'] += f" (Actual: {num_jokes_gen} cands)"


        return {"nodes": nodes, "edges": edges, "annotations": annotations, "raw_last_run_data_summary": last_run_data}