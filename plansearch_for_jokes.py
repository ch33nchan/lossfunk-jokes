
from typing import List, Dict, Any, Optional, Set, Tuple
import itertools
from.openrouter_client import OpenRouterClient # Corrected import

class PlanSearcherForJokes:
    def __init__(self, llm_client: OpenRouterClient):
        self.llm_client = llm_client
        self.transparency_data = {"observations":, "plans":, "jokes_generated":}


    def _prompt_for_observations(self, topic: str, model_name: str, existing_observations: Optional[List[str]] = None) -> List[str]:
        
        if existing_observations:
            prompt_content = (
                f"Given the topic '{topic}' and the following initial observations:\n"
                f"{'\n'.join([f'- {obs}' for obs in existing_observations])}\n\n"
                f"Brainstorm several new, non-obvious, and potentially humorous derivative observations or concepts "
                f"that build upon or combine these existing observations. Focus on finding unique angles, "
                f"contrasts, or absurdities related to '{topic}'. List each new observation on a new line."
            )
        else:
            prompt_content = (
                f"For the topic '{topic}', brainstorm a diverse list of associated concepts, facts, stereotypes, "
                f"common sayings, potential ambiguities, and inherent comedic elements. "
                f"Think about what makes '{topic}' potentially funny (e.g., irony, absurdity, wordplay opportunities). "
                f"List each observation on a new line."
            )
        
        messages = [{"role": "user", "content": prompt_content}]
        response = self.llm_client.get_completion(model_name, messages, temperature=0.8, max_tokens=300)
        if response:
            obs_list = [obs.strip() for obs in response.split('\n') if obs.strip()]
            self.transparency_data["observations"].append({
                "topic": topic, "existing_observations": existing_observations, "generated_observations": obs_list
            })
            return obs_list
        return

    def _generate_observation_combinations(self, observations: List[str], max_subset_size: int = 2) -> List]:
       
        combinations =
        for i in range(1, max_subset_size + 1):
            for subset in itertools.combinations(observations, i):
                combinations.append(subset)
        return combinations

    def _prompt_for_joke_plan(self, topic: str, observation_combo: Tuple[str,...], model_name: str) -> Optional[str]:
        
        observations_str = "\n".join([f"- {obs}" for obs in observation_combo])
        prompt_content = (
            f"Topic: '{topic}'\n"
            f"Key Observations/Elements to incorporate:\n{observations_str}\n\n"
            f"Based on these observations, devise a high-level plan or comedic strategy for a joke. "
            f"Describe the intended structure (e.g., setup-punchline, pun-based, observational, character-based) "
            f"and the core humorous mechanism. Be specific but concise. For example: "
            f"'Plan: Setup a common scenario involving {topic}, then introduce an unexpected twist based on "
            f"[{', '.join(observation_combo[:1]) if observation_combo else 'a key observation'}] for the punchline, "
            f"aiming for surprise.'"
        )
        messages = [{"role": "user", "content": prompt_content}]
        plan = self.llm_client.get_completion(model_name, messages, temperature=0.7, max_tokens=150)
        if plan:
            self.transparency_data["plans"].append({
                "topic": topic, "observation_combo": observation_combo, "generated_plan": plan
            })
        return plan

    def _prompt_for_joke_instantiation(self, topic: str, plan: str, model_name: str, critique: Optional[str] = None) -> Optional[str]:
       
        if critique:
            prompt_content = (
                f"Topic: '{topic}'\n"
                f"Original Joke Plan: {plan}\n"
                f"Critique of previous attempt: {critique}\n\n"
                f"Based on the plan and addressing the critique, generate a new, improved, and funny joke. "
                f"Ensure the joke is coherent and directly implements the core idea of the plan while learning from the critique."
            )
        else:
            prompt_content = (
                f"Topic: '{topic}'\n"
                f"Joke Plan: {plan}\n\n"
                f"Based on this plan, write a complete, funny joke. "
                f"The joke should be well-structured and deliver a clear punchline. "
                f"Focus on originality and cleverness."
            )
        messages = [{"role": "user", "content": prompt_content}]
        joke = self.llm_client.get_completion(model_name, messages, temperature=0.9, max_tokens=200)
        if joke:
             self.transparency_data["jokes_generated"].append({
                "topic": topic, "plan": plan, "critique": critique, "joke": joke
            })
        return joke

    def _prompt_for_critique(self, joke: str, plan: str, model_name: str) -> Optional[str]:
        
        prompt_content = (
            f"Joke Plan: {plan}\n"
            f"Generated Joke: \"{joke}\"\n\n"
            f"Critically evaluate this joke based on the provided plan. Is it funny? Original? Does it effectively implement the plan? "
            f"Provide specific, constructive criticism. For example, 'The setup is good, but the punchline is predictable. "
            f"It could be funnier if it subverted expectations more related to [aspect of plan].'"
        )
        messages = [{"role": "user", "content": prompt_content}]
        critique = self.llm_client.get_completion(model_name, messages, temperature=0.6, max_tokens=150)
        return critique

    def run_plansearch(self,
                       topic: str,
                       observation_model: str,
                       plan_model: str,
                       joke_model: str,
                       critique_model: Optional[str] = None,
                       num_first_order_obs: int = 5,
                       num_second_order_obs_per_combo: int = 2, # Reduced for speed
                       max_plans_to_develop: int = 5,      # Reduced for speed
                       use_critique_refinement: bool = True) -> List]:
        self.transparency_data = {"observations":, "plans":, "jokes_generated":} # Reset for new run
        print(f"Starting PLANSEARCH for topic: {topic}")
        candidate_jokes_details =

        first_order_obs = self._prompt_for_observations(topic, observation_model)
        if not first_order_obs:
            print("Failed to generate first-order observations.")
            return
        first_order_obs = first_order_obs[:num_first_order_obs]
        print(f"Generated {len(first_order_obs)} first-order observations.")

        all_observations_set: Set[str] = set(first_order_obs)
        
        first_order_combinations = self._generate_observation_combinations(first_order_obs, max_subset_size=2)
        second_order_obs_sources =

        for i, combo in enumerate(first_order_combinations):
            if len(second_order_obs_sources) >= max_plans_to_develop * 1.5: # Limit calls
                break
            
            derived_obs_list = self._prompt_for_observations(topic, observation_model, existing_observations=list(combo))
            if derived_obs_list:
                derived_obs_list = derived_obs_list[:num_second_order_obs_per_combo]
                second_order_obs_sources.append({'source_combo': combo, 'derived': derived_obs_list})
                all_observations_set.update(derived_obs_list)
        
        print(f"Total unique observations collected: {len(all_observations_set)}")

        plan_candidates_sources = first_order_combinations + \
                                  [tuple(obs_item['derived']) for obs_item in second_order_obs_sources if obs_item['derived']]
        
        developed_plans_count = 0
        for i, obs_combo_for_plan in enumerate(plan_candidates_sources):
            if developed_plans_count >= max_plans_to_develop:
                break
            if not obs_combo_for_plan: continue

           
            plan = self._prompt_for_joke_plan(topic, obs_combo_for_plan, plan_model)
            if not plan:
                continue
            
            developed_plans_count += 1
           

            joke = self._prompt_for_joke_instantiation(topic, plan, joke_model)
            if joke:
                candidate_jokes_details.append({
                    "joke_text": joke, "plan": plan, "observations_used": obs_combo_for_plan, "refined": False
                })
                
                if use_critique_refinement and critique_model:
                    critique = self._prompt_for_critique(joke, plan, critique_model)
                    if critique:
                        # print(f"Critique: {critique}")
                        refined_joke = self._prompt_for_joke_instantiation(topic, plan, joke_model, critique=critique)
                        if refined_joke and refined_joke!= joke:
                            candidate_jokes_details.append({
                                "joke_text": refined_joke, "plan": plan, "observations_used": obs_combo_for_plan, "refined": True, "critique": critique
                            })
                            
        
        print(f"PLANSEARCH finished. Generated {len(candidate_jokes_details)} candidate jokes.")
        return candidate_jokes_details

    def get_transparency_data(self) -> Dict:
        return self.transparency_data