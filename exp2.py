import boto3
import pandas as pd
import json

# Create an AWS FIS client
fis_client = boto3.client('fis')

# Function to get the list of FIS experiments
def get_fis_experiments():
    response = fis_client.list_experiments()
    return response.get('experiments', [])

# Function to extract actions and targets from the experiments list
def extract_actions_targets_from_experiments(experiments):
    actions_targets_data = []
    
    for experiment in experiments:
        experiment_id = experiment['id']
        description = experiment.get('description', '')
        state = experiment.get('state', {}).get('status', '')
        
        # Get experiment details to fetch actions and targets
        experiment_details = fis_client.get_experiment(experimentId=experiment_id)
        
        for action_name, action_details in experiment_details['experiment']['actions'].items():
            action_id = action_details.get('actionId', '')
            action_parameters = json.dumps(action_details.get('parameters', {}))
            action_state = action_details.get('state', {}).get('status', '')
            action_reason = action_details.get('state', {}).get('reason', '')

            for target_name in action_details['targets'].values():
                target_info = experiment_details['experiment']['targets'][target_name]
                resource_tags_str = json.dumps(target_info.get("resourceTags", {})) if "resourceTags" in target_info else ""
                filters_str = json.dumps(target_info.get("filters", [])) if "
