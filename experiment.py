import boto3
import pandas as pd
import json

# Create an AWS FIS client
fis_client = boto3.client('fis')

# Function to get the list of FIS experiments
def get_fis_experiments():
    experiments = []
    paginator = fis_client.get_paginator('list_experiments')
    
    for page in paginator.paginate():
        experiments.extend(page['experiments'])
    
    return experiments

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
                filters_str = json.dumps(target_info.get("filters", [])) if "filters" in target_info else ""
                
                actions_targets_data.append({
                    'experimentId': experiment_id,
                    'description': description,
                    'state': state,
                    'actionName': action_name,
                    'actionId': action_id,
                    'actionParameters': action_parameters,
                    'actionState': action_state,
                    'actionReason': action_reason,
                    'targetName': target_name,
                    'resourceType': target_info.get("resourceType", ""),
                    'resourceArns': json.dumps(target_info.get("resourceArns", [])),
                    'selectionMode': target_info.get("selectionMode", ""),
                    'resourceTags': resource_tags_str,
                    'filters': filters_str
                })
    
    return actions_targets_data

# Function to convert the extracted data to a CSV file
def convert_to_csv(data, filename='fis_actions_targets.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"CSV file '{filename}' created successfully.")

# Get the list of FIS experiments
experiments = get_fis_experiments()

# Extract the actions and targets data from the experiments list
actions_targets_data = extract_actions_targets_from_experiments(experiments)

# Convert the actions and targets data to a CSV file
convert_to_csv(actions_targets_data)
