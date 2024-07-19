import boto3
import pandas as pd
import json

# Create an AWS FIS client
fis_client = boto3.client('fis')

# Function to get the list of FIS experiments
def get_fis_experiments():
    response = fis_client.list_experiments()
    return response.get('experiments', [])

# Function to extract experiment details excluding targets and actions
def extract_experiment_details(experiments):
    experiment_details = []
    
    for experiment in experiments:
        experiment_details.append({
            'experimentId': experiment['id'],
            'description': experiment.get('description', ''),
            'state': experiment.get('state', {}).get('status', ''),
            'creationTime': experiment.get('creationTime', ''),
            'tags': json.dumps(experiment.get('tags', {}))
        })
    
    return experiment_details

# Function to extract actions and targets from the experiments list
def extract_actions_targets_from_experiments(experiments):
    actions_targets_data = []
    
    for experiment in experiments:
        experiment_id = experiment['id']
        
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

# Function to convert the extracted data to CSV files
def convert_to_csv(experiment_data, actions_targets_data, experiment_filename='fis_experiments.csv', actions_targets_filename='fis_actions_targets.csv'):
    experiment_df = pd.DataFrame(experiment_data)
    experiment_df.to_csv(experiment_filename, index=False)
    
    actions_targets_df = pd.DataFrame(actions_targets_data)
    actions_targets_df.to_csv(actions_targets_filename, index=False)
    
    print(f"CSV files '{experiment_filename}' and '{actions_targets_filename}' created successfully.")

# Get the list of FIS experiments
experiments = get_fis_experiments()

# Extract the experiment details excluding targets and actions
experiment_data = extract_experiment_details(experiments)

# Extract the actions and targets data from the experiments list
actions_targets_data = extract_actions_targets_from_experiments(experiments)

# Convert the extracted data to CSV files
convert_to_csv(experiment_data, actions_targets_data)
