
I'm addressing two main topics:

1-Retrieving and processing data from Dynatrace API endpoints using Python.

2-Creating a manual metric on a Linux server using Python and sending it to the Dynatrace 
for visualization, as well as generating alerts in case of adverse conditions.


Expalanation of Dynatrace API python code

This Python script is designed to retrieve host, process, process group, and service data from Dynatrace APIs.
The script performs the following steps:

1. API calls: It sends HTTP GET requests to various Dynatrace API endpoints (hosts, processes, process groups, and services) 
to fetch data about the Dynatrace infrastructure.

2. Data transformation: It transforms the retrieved data into JSON format.

3. Data selection: It selects the desired columns from the JSON data and cleans up characters such as "[ ]" and "{ }" as needed.

4. Data appending: It appends the selected data to an empty list.

5. DataFrame creation: It converts the data from the list into DataFrame structures

6. DataFrame manipulation: It uses merge functions to add certain columns from other DataFrames to Process, process group, and service DataFrames. 
This enables the addition of desired data to the DataFrames.

7. Excel creation: The created DataFrames are converted to Excel files (.xlsx) and written to the specified file path in the operating system.


Expalanation of Dynatrace ingest python code

This Python script is designed to send metrics manually to Dynatrace. It sends the status (up/down) of selected 
network interfaces on the server to Dynatrace at regular intervals. The code runs within a while loop, continuously 
sending these metrics to Dynatrace at the specified time interval. The dynatrace_ingest tool is used for this process.
