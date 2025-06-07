
from flask import Flask, request, jsonify
from.joke_pipeline_manager import JokePipelineManager 
from.transparency_module import TransparencyProvider
import os

app = Flask(__name__)

app.config = {} 

transparency_provider = TransparencyProvider()

@app.route('/generate_jokes', methods=)
def generate_jokes_endpoint():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    topic = data.get('topic')
    user_api_key = data.get('user_openrouter_api_key')
    llm_choices = data.get('llm_choices', {})
    num_top_jokes = data.get('num_top_jokes', 3)

    if not topic or not user_api_key:
        return jsonify({"error": "Missing 'topic' or 'user_openrouter_api_key'"}), 400

    try:
      
        pipeline_manager = JokePipelineManager(openrouter_api_key=user_api_key) 
        top_jokes = pipeline_manager.generate_and_evaluate_jokes(
            topic,
            user_llm_choices,
            num_top_jokes=int(num_top_jokes)
        )
        
    
        app.config = pipeline_manager.get_last_run_transparency_data()

        return jsonify({"top_jokes": top_jokes}), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

@app.route('/transparency_info', methods=)
def transparency_info_endpoint():
    info_type = request.args.get('type') 
    
    if info_type == 'plansearch_code':
        details = transparency_provider.get_plansearch_code_details()
        return jsonify(details), 200
    elif info_type == 'pipeline_visualization':
        last_run_data_for_viz = app.config.get('LAST_RUN_DATA', None)
        viz_data = transparency_provider.get_pipeline_visualization_data(last_run_data_for_viz)
        return jsonify(viz_data), 200
    else:
        return jsonify({"error": "Invalid transparency info type requested. Use 'plansearch_code' or 'pipeline_visualization'."}), 400
