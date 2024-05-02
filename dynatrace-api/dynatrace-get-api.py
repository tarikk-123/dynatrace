
import requests
import pandas as pd

base_url = "https://10.100.13.15/e/bc2ebc03-bcfb-466c-8f42-ffa5bb4786ee"
host_url= f"{base_url}/api/v1/entity/infrastructure/hosts"
process_url = f"{base_url}/api/v1/entity/infrastructure/processes"
process_group_url = f"{base_url}/api/v1/entity/infrastructure/process-groups"
service_url  = f"{base_url}/api/v1/entity/services"
token = headers = {
        "Authorization": "Api-Token dt0c01.HFO6FKI7IKUYXPKJJPR6UPKY.34QTLOSAET63XSN5YF3Q44TZMZHTKIIZNQJXYJ5F3XJ5U3VATYIYMHE5IABHDNBL"
    }

path =  "/home/tarik/Desktop/dynatrace/"
hosts_excel_path = f"{path}dynatrace_hosts.xlsx"
processes_excel_path = f"{path}dynatrace_processes.xlsx"
processes_group_excel_path = f"{path}dynatrace_processes_group.xlsx"
service_excel_path = f"{path}dynatrace_service.xlsx"



def get_data(url):

    response = requests.get(url, headers=token, verify=False)

    if response.status_code == 200:
        return response.json()
    else:
        print("Request failed with status code:", response.status_code)
        return None


def get_hosts():
    json_data = get_data(host_url)

    if json_data:
        data_to_extract = []

        for host in json_data:
            ip_addresses = ', '.join(host.get("ipAddresses", []))
            host_info = {
                "entityId": host.get("entityId"),
                "displayName": host.get("displayName"),
                "tags": host.get("tags"),
                "ipAddresses": ip_addresses
            }
            data_to_extract.append(host_info)

        host_df = pd.DataFrame(data_to_extract)
        host_df.to_excel(hosts_excel_path, index=False)
        return host_df


def get_processes():
    json_data = get_data(process_url)

    if json_data:
        data_to_extract = []

        for host in json_data:
            runs_on_list = ', '.join(host.get("fromRelationships", {}).get("isProcessOf", []))
            runs_on_list2 = ', '.join(host.get("fromRelationships", {}).get("isInstanceOf", []))

            host_info = {
                "entityId": host.get("entityId"),
                "displayName": host.get("displayName"),
                "softwareTechnologies": host.get("softwareTechnologies"),
                "fromRelationships.isProcessOf": runs_on_list,
                "fromRelationships.isInstanceOf": runs_on_list2,
                "tags": host.get("tags")
            }
            data_to_extract.append(host_info)

        process_df = pd.DataFrame(data_to_extract)
        return process_df
        
def get_processgroups():

    json_data = get_data(process_group_url)


    if json_data:
        data_to_extract = []

        for host in json_data:
            runs_on_list = host.get("fromRelationships", {}).get("runsOn", [])
            runs_on_list2 = host.get("toRelationships", {}).get("isInstanceOf", [])

            runs_on_string = ', '.join(runs_on_list)
            runs_on_string2 = ', '.join(runs_on_list2)

            host_info = {
                "entityId": host.get("entityId"),
                "displayName": host.get("displayName"),
                "softwareTechnologies": host.get("softwareTechnologies"),
                "fromRelationships.runsOn": runs_on_string,
                "toRelationships.isInstanceOf": runs_on_string2,
                "tags": host.get("tags")
            }
            data_to_extract.append(host_info)

        processgroup_df = pd.DataFrame(data_to_extract)
        return processgroup_df

def get_services():

    json_data = get_data(service_url)

    if json_data:
       
       data_to_extract = []

       for host in json_data:
            
            runs_on_list = host.get("fromRelationships", {}).get("runsOn", [])
            runs_on_ids = [f"PROCESS_GROUP-{item.split('-')[-1]}" for item in runs_on_list if item]
            runs_on_ids_str = ', '.join(runs_on_ids)

            host_info = {
                "entityId": host.get("entityId"),
                "displayName": host.get("displayName"),
                "softwareTechnologies": host.get("softwareTechnologies"),
                "webApplicationId": host.get("webApplicationId"),
                "webServerName": host.get("webServerName"),
                "fromRelationships_runsOn": runs_on_ids_str,
                "tags": host.get("tags")
            }

            data_to_extract.append(host_info)

       service_df = pd.DataFrame(data_to_extract)
       return service_df

def merge_between_host_and_process(host,process):
    host_df =  host
    process_df = process

    merged_df = pd.merge(
        process_df, host_df, how='left', left_on='fromRelationships.isProcessOf', right_on='entityId'
    )
    merged_df['ipAddress'] = merged_df['ipAddresses'].fillna('')
    merged_df = merged_df.drop(columns=['entityId_y', 'displayName_y', 'ipAddresses', 'tags_y'])
    merged_df = merged_df.rename(columns={'entityId_x': 'entityId', 'displayName_x': 'displayName', 'tags_x': 'tags'})

    merged_df.to_excel(processes_excel_path, index=False)
    
def merge_between_host_and_processgroup(host,process_group):
    host_df = host
    process_df = process_group

    process_df['fromRelationships.runsOn'] = process_df['fromRelationships.runsOn'].str.split(', ')
    process_df = process_df.explode('fromRelationships.runsOn')

    merged_df = pd.merge(
        process_df, host_df, how='left', left_on='fromRelationships.runsOn', right_on='entityId'
    )
    
    merged_df['ipAddress'] = merged_df['ipAddresses'].fillna('')
    merged_df = merged_df.drop(columns=['entityId_y', 'displayName_y', 'ipAddresses', 'tags_y'])
    merged_df = merged_df.rename(columns={'entityId_x': 'entityId', 'displayName_x': 'displayName', 'tags_x': 'tags'})

    merged_df = merged_df.groupby('entityId',sort=False).agg({
        'displayName': 'first',
        'softwareTechnologies': 'first',
        'fromRelationships.runsOn': lambda x: ', '.join(x),
        "toRelationships.isInstanceOf": 'first',
        "tags":'first',
        'ipAddress': lambda x: ', '.join(x)


    }).reset_index()

    merged_df.to_excel(processes_group_excel_path, index=False)

def merge_between_host_and_service(service_data):
    group_df = pd.read_excel(processes_group_excel_path)
    process_df = service_data

    merged_df = pd.merge(
        process_df, group_df, how='left', left_on='fromRelationships_runsOn', right_on='entityId'
    )
    merged_df['ipAddress'] = merged_df['ipAddress'].fillna('')
    merged_df = merged_df.drop(columns=['entityId_y', 'displayName_y', 'softwareTechnologies_y','fromRelationships.runsOn',  'tags_y'])
    merged_df = merged_df.rename(columns={'entityId_x': 'entityId', 'displayName_x': 'displayName', 'softwareTechnologies_x': 'softwareTechnologies', 'tags_x': 'tags'})

    merged_df.to_excel(service_excel_path, index=False)

def main():
    host_data = get_hosts()
    process_data = get_processes()
    merge_between_host_and_process(host_data,process_data)
    process_group_data = get_processgroups()
    merge_between_host_and_processgroup(host_data,process_group_data)
    service_data = get_services()
    merge_between_host_and_service(service_data)


if __name__ == "__main__":
    main()


