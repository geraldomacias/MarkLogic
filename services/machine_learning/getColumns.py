"""
Copyright 2019 Team Mark

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# coding: utf-8

# In[3]:


import pandas as pd
import json
import glob
import sys


# * Eventually we will want to parse from the s3 bucket

# In[9]:


sports = []


# In[10]:


football = []
files = []
for filename in glob.iglob('../../../rawDataSets/football/' + "**", recursive=True):
    files.append(filename)
    if ".csv" in filename:
        data = pd.read_csv(filename).columns
        for d in data:
            d = d.replace('_', '').replace(' ', '').replace('-', '').lower()
            sports.append({'football': d})
            #football.append(d)
                
#sports['football'] = football


# In[12]:


#sports


# In[14]:


basketball = []
files = []
for filename in glob.iglob('../../../rawDataSets/basketball/' + "**", recursive=True):
    files.append(filename)
    if ".csv" in filename and 'TeamSpellings.csv' not in filename:
        data = pd.read_csv(filename).columns
        for d in data:
            d = d.replace('_', '').replace(' ', '').replace('-', '').lower()
            sports.append({'basketball': d})
            #basketball.append(d)
                
#sports['basketball'] = basketball


# In[15]:


hockey = []
files = []
for filename in glob.iglob('../../../rawDataSets/hockey/' + "**", recursive=True):
    files.append(filename)
    if ".csv" in filename:
        data = pd.read_csv(filename, error_bad_lines=False).columns
        for d in data:
            d = d.replace('_', '').replace(' ', '').replace('-', '').lower()
            sports.append({'hockey': d})
            #hockey.append(d)
                
#sports['hockey'] = hockey


# In[16]:


baseball = []
files = []
for filename in glob.iglob('../../../rawDataSets/baseball/' + "**", recursive=True):
    files.append(filename)
    if ".csv" in filename:
        data = pd.read_csv(filename, error_bad_lines=False).columns
        for d in data:
            d = d.replace('_', '').replace(' ', '').replace('-', '').lower()
            sports.append({'baseball': d})
            #baseball.append(d)
                
#sports['baseball'] = baseball


# In[17]:


soccer = []
files = []
for filename in glob.iglob('../../../rawDataSets/soccer/' + "**", recursive=True):
    files.append(filename)
    if ".csv" in filename:
        data = pd.read_csv(filename, error_bad_lines=False, encoding='latin-1').columns
        for d in data:
            d = d.replace('_', '').replace(' ', '').replace('-', '').lower()
            sports.append({'soccer': d})
            #soccer.append(d)
                
#sports['soccer'] = soccer


# In[18]:


print(json.dumps(sports, indent=4, separators=(',', ': ')))

