# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.15.2
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Description
#
# This notebook is used for prototyping, testing, and researching different services that are able to retrieve emails from a LinkedIn profile. The goal is to optimize speed. Emails can be either personal or professional.

# %%
# imports

import requests

# %% [markdown]
# ## Phantom Buster
#
# - Launched the email finder phantom manually though the site
# - Successfully found the personal email of a first degree connection in 1 minute and 23 seconds
# - Failed to find personal email and professional email of a second degree connection in 32 seconds

# %% [markdown]
# ### Proxycurl

# %%
api_key = ""
headers = {"Authorization": "Bearer " + api_key}
api_endpoint = "https://nubela.co/proxycurl/api/contact-api/personal-email"
params = {
    "linkedin_profile_url": "https://www.linkedin.com/in/luciana-lixandru-11042875/",
    "email_validation": "include",
    "page_size": "0",
}
response = requests.get(api_endpoint, params=params, headers=headers, timeout=30)
print(response.json())

# %%
api_key = ""
headers = {"Authorization": "Bearer " + api_key}
api_endpoint = "https://nubela.co/proxycurl/api/linkedin/profile/email"
params = {
    "linkedin_profile_url": "https://www.linkedin.com/in/luciana-lixandru-11042875/",
    "callback_url": "",
}
response = requests.get(api_endpoint, params=params, headers=headers, timeout=30)
print(response.json())

# %% [markdown]
# ### Hunter.io

# %%
api_key = ""
domain = "sequoiacap.com"
first_name = "Luciana"
last_name = "Lixandru"
api_endpoint = f"https://api.hunter.io/v2/email-finder?domain={domain}&first_name={first_name}&last_name={last_name}&api_key={api_key}"
response = requests.get(api_endpoint, timeout=30)
print(response.json())

# %% [markdown]
# ### Dropcontact.com

# %%
api_key = ""
response = requests.post(
    "https://api.dropcontact.io/batch",
    json={
        "data": [
            {
                "first_name": "Luciana",
                "last_name": "Lixandru",
                "company": "Sequoia Capital",
            }
        ],
        "siren": True,
        "language": "en",
    },
    headers={"Content-Type": "application/json", "X-Access-Token": api_key},
)
response.json()

# %%
request_id = "nwncnfkrfbcikjf"
response = requests.get(
    "https://api.dropcontact.io/batch/{}".format(request_id),
    headers={"X-Access-Token": api_key},
)
response.json()

# %% [markdown]
# ### Snov.io - Paid API use only
