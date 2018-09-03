# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
import json
import time
import datetime
#Credentials
USERNAME="adityatajne94@gmail.com"
PASSWORD="Nanda@1970"

#Varaibles
repo_data=[]
repo_id=[]
count_open_issue=[]
count_forks=[]
count_watchers=[]
PULL_DATA=[]
Pull_json_data=[]  
Final_json_data=[]
contri_count = []
push_delta=[]
contributor_list=[]
prob_pull=[]
prob_contributors=[]
temp=[]
currenttime = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.localtime())


def cal_total_page(header_data):
    if 'Link' in header_data:
        print(header_data['Link'])
        target_data=header_data['Link'].split(",")
        id_no=target_data[1].find("&")
        total_page_val=target_data[1][id_no-2:id_no]
        if '=' in total_page_val:
            page_value=total_page_val.replace("=",'')
            total_page=int(page_value)
            return total_page
        else:
            total_page=int(total_page_val)
            return total_page
    else:
        return 0
#Function for features at repo level
def fatures_at_repo_count(repo_data):
    for i in range(len(repo_data)):
        #count for open issue per repository    
        count_open_issue.append(repo_data[i]['open_issues_count'])    
        #count for number of forks
        count_forks.append(repo_data[i]['forks_count'])
        #count for watchers per repo
        count_watchers.append(repo_data[i]['watchers_count'])
        #Tme since last push on repository    
        a = datetime.datetime.strptime(repo_data[i]['pushed_at'], "%Y-%m-%dT%H:%M:%SZ")
        b = datetime.datetime.strptime(currenttime, "%Y-%m-%dT%H:%M:%SZ")
        serconds_last_push = (b-a).total_seconds()
        push_delta.append(serconds_last_push)
        #PUll Data
        Pull_URL=repo_data[i]['pulls_url']
        PULL_HEADER_URL=Pull_URL.replace('{/number}','?page=1&per_page=100&state=all')
        cal_page= requests.get(url=PULL_HEADER_URL,auth=(USERNAME,PASSWORD))
        header_data=cal_page.headers
        total_page=cal_total_page(header_data)
        print(total_page)
        PULL_raw_data=[]
        for j in range(total_page):
            print("Processing total pull data inside one repo...")
            target_str='?page=%d&per_page=100&state=all'%j
            PULL_URL = Pull_URL.replace('{/number}', target_str)
            PULL_raw_data.append(requests.get(url=PULL_URL,auth=(USERNAME,PASSWORD)).json())
        print(len(PULL_raw_data))
        for k in range(len(PULL_raw_data)):
            print("Pull raw data count %d"%k)
            print(len(PULL_raw_data[k]))
            for m in range(len(PULL_raw_data[k])):
                
                temp.append(PULL_raw_data[k][m])
        PULL_DATA.append(temp)   
        #PULL_URL=Pull_URL.replace('{/number}','?state=all')
        #PULL_DATA.append(requests.get(url=PULL_URL,auth=(USERNAME,PASSWORD)).json())
        
def input_repo():
    input1 = input("Enter the number of repos data you want?")
    input_no_of_repo = int(input1)
    return input_no_of_repo

def repos_data(resource_data):
    input_no_of_repo = input_repo()
    while input_no_of_repo > 3000 or input_no_of_repo < 0:
        print("Please enter the number of repos below 3000 and greater than 0")
        input_no_of_repo=input_repo()
    for i in range(input_no_of_repo):#HOw many repo data we need from 11k repo
        jsondata=json.loads(resource_data[i].decode("ISO-8859-1"))
        #Extract☻ repo URL from data
        main_data=requests.get(jsondata['repo']['url'],auth=(USERNAME,PASSWORD))
        if main_data.status_code == 200:
            repo_data.append(main_data.json())
            #Repo id extraction for our reference
            repo_id.append(jsondata['repo']['id'])
            #Get the contributors list
            con_url= jsondata['repo']['url'] + "/contributors"
            actual_count=[]
            count_URL=requests.get(url=con_url,auth=(USERNAME,PASSWORD))
            if count_URL.status_code == 204:
                contributor_list.append('NA')
                contri_count.append(0)
            else:    
                count_con=count_URL.json()
                if type(count_con) is list:
                    for j in range(len(count_con)):
                        if 'login' in count_con[j]:    
                            actual_count.append(count_con[j]['login'])
                        else:
                            actual_count.append('NA')
                    contributor_list.append(actual_count)    
                    contri_count.append(len(actual_count))
                else:
                    contributor_list.append('NA')
                    contri_count.append(0)
                   
#PULL_DATA contains data of all pull request regarding to that particular repo
#label 1 :- if pull request is merge and considered as accepted.
#label 0:- pull request is not merge and state is closed so rejected
#label -1:- pull request is not merge and state is open so open                    
def label(PULL_DATA):
    #Get the correct label URL
    label_url = PULL_DATA['url']+"/merge"
    #requests.get(uel,auth) gives only the response. but requests.get(uel,auth).json gives json data of resonse 
    label_data = requests.get(url=label_url,auth=(USERNAME,PASSWORD))
    label_status = label_data.status_code
    #condition for accepte. 204 is http status code for no content found
    if label_status == 204:
        return 1
    #404 not found so gets rejected on the basis of state value
    if label_status == 404:
        if PULL_DATA['state'] == 'closed':#rejected
            return 0
        elif PULL_DATA['state'] == 'open':#open
            return -1
    else:
        return 2
#function for calculate no_of file change and nos of additions and deletions    
def diff_status(PULL_URL):
    PULL_URL=PULL_URL+"/files"
    PATCH_DATA = requests.get(url=PULL_URL,auth=(USERNAME,PASSWORD)).json()
    DATA=[]
    insertions=0
    deletions=0
    #checking len of data to ensure that correct data will return
    if len(PATCH_DATA)>0:
        for i in range(len(PATCH_DATA)):
            #checking condition for data that is not releveant to us and in every such instance that 
            #data contains message key. verified this key many times.
            if 'message' in PATCH_DATA:
                DATA.append(0)
                DATA.append(insertions)
                DATA.append(deletions)
                return DATA
            else:
                #calculating additions and insertions
                insertions=insertions+PATCH_DATA[i]['additions']
                insertions=insertions+0
                deletions=deletions+PATCH_DATA[i]['deletions']
                deletions=deletions+0
        DATA.append(len(PATCH_DATA))
        DATA.append(insertions)
        DATA.append(deletions)  
        return DATA
    else:
        DATA.append(0)
        DATA.append(insertions)
        DATA.append(deletions)
        return DATA
#function for commits calcularion    
def commits_count(URL):
    count=requests.get(url=URL,auth=(USERNAME,PASSWORD)).json()
    return count

#Creating Final dictionary
def creating_json_data(length):
    final_data=[]
    for i in range(len(count_forks)):
        final_data.append({
        'id' : repo_id[i],
        'contributors_count' : contri_count[i],
        'open_issue_count' : count_open_issue[i],
        'forks_count' : count_forks[i],
        'watchers_count' : count_watchers[i],
        'Pushed_delta' : push_delta[i],
        'contrib_prob' : prob_contributors[i],
        'repo_prob' : prob_pull[i],
        'pull_data' : Pull_json_data[i]

        })
    return final_data

#calculating probability for contri count    
def prob_count_contributors(PULL_DATA):
    print("count prob %de"%len(PULL_DATA))
    for i in range(len(PULL_DATA)):
        print("count %d"%i)
        if ' ' not in PULL_DATA[i]:
            total_merged = 0
            contributors_merged= 0
            pulls_closed = 0
            contributors_prob = 0
            pull_prob = 0
            for j in range(len(PULL_DATA[i])):
                if (PULL_DATA[i][j]['state'] == 'closed'):
                     pulls_closed+=1
                if(PULL_DATA[i][j]['merged_at']!=None):                
                     total_merged+=1     
                if(PULL_DATA[i][j]['merged_at']!=None and PULL_DATA[i][j]['user']['login'] in contributor_list[i] ):
                     contributors_merged+=1       
            if(total_merged!=0):
                contributors_prob = contributors_merged/total_merged 
                prob_contributors.append(contributors_prob)
            else:
                prob_contributors.append(0)
            if(pulls_closed!=0):
                pull_prob = total_merged/pulls_closed 
                prob_pull.append(pull_prob)
            else:
                prob_pull.append(0)
        else:
           
            prob_contributors.append(0)
            prob_pull.append(0)
            
#Gathering data at PUll level
def PULL_LEVEL_DATA(PULL_DATA):
    
    print("Length of pull data to be collected from %d repos"%len(PULL_DATA))
    for i in range(len(PULL_DATA)):
        print("Pull level data collection Processing....")
    #if no objectes are there
        if ' ' not in PULL_DATA[i]:
            file_json_data=[]
            for j in range(len(PULL_DATA[i])):
                pull_id=PULL_DATA[i][j]['id']#Pull id for our ref
                no_of_file_changed=0
                no_of_insertion=0
                no_of_deletion=0
                commit_count=0
                acc_label="NA" #for our ref
                if 'url' in PULL_DATA[i][j]:
                    PULL_URL=PULL_DATA[i][j]['url']
                    #status of pull request
                    acc_label=label(PULL_DATA[i][j])
                    #file level data
                    DATA=diff_status(PULL_URL)
                    #data1=DATA[0].strip().split(" ")
                    no_of_file_changed=DATA[0]
                    no_of_insertion=DATA[1]
                    no_of_deletion=DATA[2]
                if 'commits_url' in PULL_DATA[i][j]:
                    URL=PULL_DATA[i][j]['commits_url']
                    commit_data=commits_count(URL)
                    commit_count=len(commit_data)   
                file_json_data.append({
                   'Pull_id' : pull_id,
                   'label' : acc_label,
                   'no_of_file_change' : no_of_file_changed,
                   'no_of_insertion' : no_of_insertion,
                   'no_of_deletion' : no_of_deletion,
                   'no_of_commits' : commit_count
                    }) 
            
        else:
            Pull_json_data.append([{
                   'Pull_id' : 0,
                   'label' : 0,
                   'no_of_file_change' : 0,
                   'no_of_total_line_changed' : 0,
                   'no_of_commits' : 0
                   }])
            
        Pull_json_data.append(file_json_data)
        
#Explicitly collected repos data. Containing 11k repos url. But the data that 
#we got from these repos will be dynamic. We will hit url of these repo 
#at github server at runtime.        
org_data=open("git_archieve_data_repos.json","rb")
resource_data=list(org_data)
print("Successfully collected resource data.")
#travesring and collcting some features at repo level    
repos_data(resource_data)  
print("Successfully collected repos data.\n")  
#More features at repo level
fatures_at_repo_count(repo_data)
print("Successfully collected repos count data.\n")
prob_count_contributors(PULL_DATA) 
print("Successfully collected repo contri count data.\n")
#Features at Pull level
PULL_LEVEL_DATA(PULL_DATA) 
print("Successfully collected pull level data.\n")
#final json data      
Final_json_data=creating_json_data(len(count_forks))
print("Successfully created json data.\n")
#dumping of all data into one json file                                                                                                                                            
with open('Extracted_features2.json', 'w') as outfile:  
   json.dump(Final_json_data, outfile)   
print("Succesfull completed data extraction.") 
org_data.close()
outfile.close()  