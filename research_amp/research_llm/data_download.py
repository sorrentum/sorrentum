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
# # Data Download
#
# We deal with downloading data from the following sources:
# - [goperigon.com](https://goperigon.com)
# - [newsdata.io](https://newsdata.io)
# - [mediastack.com](https://mediastack.com)
# - [thenewsapi.com](https://thenewsapi.com)
# - [marketaux.com](https://marketaux.com)
#

# %%
import requests
import logging
import json
import pandas as pd
import numpy as np
import re
from datetime import datetime

_LOG = logging.getLogger(__name__)

# %%
# Set the display options for the dataframes
pd.set_option('display.max_columns', None)  
pd.set_option('display.max_colwidth', None)  
pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.colheader_justify', 'right')
pd.set_option('display.width', 100)


# %% [markdown]
# ## goperigon.com pipeline

# %%
class goperigonPipeline:
    """
    Handles fetching data from the goperigon.com API.
    """
    def __init__(self, api_key: str = 'f745aea8-78bf-4a63-b98d-ba22320b90ad'):
        """
        Initializes the pipeline.

        :param api_key: API key for authentication.
        """
        self.api_key = api_key
        self.base_url = "https://api.goperigon.com/v1/"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        _LOG.debug(f"{self.__class__.__name__} initialized with API key: {api_key}")

    def set_query_params(self, endpoint: str = 'all', **kwargs) -> None:
        """
        Specify the API endpoint and the query parameters for fetching data.

        :param endpoint: The API endpoint to fetch data from.
            - 'all'        : Provides functionality for searching and filtering all 
                             news articles available on the API.
            - 'stories/all': Fetches data from all the sources.
            - 'sources'    : Provides functionality to search and filter for media 
                             sources from around the world.
            - 'journalists': Provides functionality for searching and filtering all journalists 
                             available on the database. 
            - 'people/all' : Search and retrieve additional information on known persons that 
                             exist within Perigon's 
                             entity database and as referenced in any article response object.
            - 'companies'  : Search and retrieve additional information on companies that exist within Perigon's 
                             entity database and as referenced in any article response object.
        :param **kwargs: The query parameters to be passed. E.g., 'category', 'topic', etc. Visit 
                        `https://docs.goperigon.com/docs/getting-started` for more information on query params for each endpoint.
        """
        # Check if kwargs is empty and assign default query params.
        if not kwargs:  
            self.params = {
            "category": 'Finance',
            "topic": 'Cryptocurrency'
            }
        else:
            self.params = kwargs
        # Assign the input endpoint as an instance variable.
        if endpoint in ['all', 'stories/all', 'sources', 'journalists', 'people/all', 'companies']:
            self.endpoint = endpoint
        else:
            raise ValueError(f"Invalid endpoint: {endpoint}")
    
    def __process_data(self, response) -> pd.DataFrame:
        """
        Clean and store the JSON response in a DataFrame.
        
        :param response: JSON response of the API request.
        :return: Dataframe of the JSON response.
        """
        # Convert the JSON response into a dataframe.
        for article in response['articles']:
            for column in ['title', 'description', 'summary']:
                if article[column] is not None:
                    # Replace newline characters with space.
                    article[column] = article[column].replace("\n", " ")
                    # Replace multiple spaces with a single space.
                    article[column] = re.sub(r"\s+", " ", article[column])
                    # Strip leading and trailing spaces.
                    article[column] = article[column].strip()
        df = pd.json_normalize(response['articles'])
        # Convert dates to datetime objects.
        for column in ['pubDate', 'addDate', 'refreshDate']:
            df[column] = pd.to_datetime(df[column])
            # Check if datetime objects are tz-aware; if not, localize to UTC before converting.
            if df[column].dt.tz is None:
                df[column] = df[column].dt.tz_localize('UTC')
            df[column] = df[column].dt.tz_convert(None)
        # Unpack column values.
        for column in ['keywords', 'topics', 'categories', 'entities']:
            exploded_df = df.explode(column)
            # Normalize the data in column.
            normalized_df = pd.json_normalize(exploded_df[column])
            # Format strings to be enclosed in double quotes.
            normalized_df = normalized_df.map(lambda x: f'"{x}"')
            # Aggregate the values by the index.
            aggregated = normalized_df.groupby(by=exploded_df.index).agg(list)
            # Rename the columns to follow the format "{column}.{key}".
            aggregated.columns = [column + "." + col for col in aggregated.columns]
            # Drop the original column.
            df = df.drop(column, axis=1)
            # Merge or concatenate this aggregated data back to your original DataFrame
            df = df.join(aggregated)
        return df 
        
    def fetch_data(self) -> pd.DataFrame:
        """
        Fetches data from a specified endpoint of the goperigon.com API.

        :return: Dataframe of the JSON response from the API.
        """
        # Create the URL to fetch the data specifying the endpoint.
        url = self.base_url + self.endpoint
        # Fetch data from the API endpoint with the passed parameters.
        try:
            response = requests.get(url=url, headers=self.headers, params=self.params)
            _LOG.debug(f"Fetching data from {response.request.url}")
            response.raise_for_status()
            _LOG.info("Data fetched successfully.")
            self.json_response = response.json()
        except requests.RequestException as e:
            _LOG.error(f"Error fetching data: {e}")
            raise
        # Compile the data in a dataframe.
        df = self.__process_data(self.json_response)
        return df
        


# %% [markdown]
# ### Sample data
#

# %%
datapipeline_1 = goperigonPipeline()
datapipeline_1.set_query_params()
df1 = datapipeline_1.fetch_data()
df1.head()


# %% [markdown]
# ## newsdata.io pipeline

# %%
class newsdataPipeline:
    """
    Handles fetching data from the newsdata.io API. 
    """
    def __init__(self, api_key: str = 'pub_41599cecccb2e7df362a6da41983f3f8729dd'):
        """
        Initializes the pipeline. 

        :param api_key: API key for authentication.
        """
        self.base_url = 'https://newsdata.io/api/1/'
        self.headers = {"X-ACCESS-KEY": api_key}
        _LOG.debug(f"{self.__class__.__name__} initialized with API key: {api_key}")

    def set_query_params(self, endpoint: str = 'news', **kwargs) -> None:
        """
        Specify the query parameters for fetching data. 
        
        :param endpoint: The API endpoint to fetch data from.
            - 'news'    : Provides access to the latest and breaking news upto the past 48 hrs.
            - 'crypto'  : Provided crypto related news and blog data.
            - 'archive' : Provides access to the old news data upto past 2 years.
            - 'sources' : Provides names of randomly selected 100 domains from a country, category or/and language.
        :param **kwargs: The query parameters to be passed. Visit `https://newsdata.io/documentation` 
                         for more information on query params for each endpoint.
        """
        # Check if kwargs is empty and assign default values.
        if not kwargs:
            self.params = {
                'q': "cryptocurrency"
                 }   
        else:
            self.params = kwargs
         # Assign the input endpoint as an instance variable.
        if endpoint in ['news', 'crypto', 'archive', 'sources']:
            self.endpoint = endpoint
        else:
            raise ValueError(f"Invalid endpoint: {endpoint}")   
    
    def __process_data(self, response) -> pd.DataFrame:
        """
        Clean and store the JSON response in a DataFrame.
        
        :param response: JSON response of the API request.
        :return: Dataframe of the JSON response.
        """
        # Convert the JSON response into a dataframe.
        for article in response['results']:
            for column in ['title', 'description', 'content']:
                if article[column] is not None:
                    # Replace newline characters with space
                    article[column] = article[column].replace("\n", " ")
                    # Replace multiple spaces with a single space
                    article[column] = re.sub(r"\s+", " ", article[column])
                    # Strip leading and trailing spaces
                    article[column] = article[column].strip()
        df = pd.json_normalize(response['results'])
        # Convert dates to datetime objects.
        for column in ['pubDate']:
            df[column] = pd.to_datetime(df[column])
            # Check if datetime objects are tz-aware; if not, localize to UTC before converting
            if df[column].dt.tz is None:
                df[column] = df[column].dt.tz_localize('UTC')
            df[column] = df[column].dt.tz_convert(None)
        return df 
        

    def fetch_data(self) -> dict:
        """
        Fetches news data from NewsData.io.

        :return: The JSON response from the API. 
        """
        # Create the URL to fetch the data specifying.
        url = self.base_url + self.endpoint
        # Fetch data from the API with the passed parameters.
        try:
            response = requests.get(url=url, headers=self.headers, params=self.params)
            _LOG.debug(f"Fetching data from {response.request.url}")
            response.raise_for_status()
            _LOG.info("Data fetched successfully.")
            self.json_response = response.json()
        except requests.RequestException as e:
            _LOG.error(f"Error fetching data: {e}")
            raise
        # Compile the data in a dataframe.
        df = self.__process_data(self.json_response)
        return df



# %% [markdown]
# ### Sample Data

# %%
datapipeline_2 = newsdataPipeline()
datapipeline_2.set_query_params()
df_newsdata = datapipeline_2.fetch_data()
df_newsdata.head()


# %% [markdown]
# ## thenewsapi.com pipeline

# %%
class newsapiPipeline:
    """
    Handles fetching data from the thenewsapi.com API.
    """
    def __init__(self, api_key: str = 'Nr11NvvuUR3VkVqFbWQpDFxdAA9wClTkofsFtQ9l'):
        """
        Intializes the pipeline.

        :param api_key: API key for authentication.
        """
        # Assign the passed API to an instance variable.
        self.api_key = api_key
        self.base_url = 'https://api.thenewsapi.com/v1/news/'
        _LOG.debug(f"{self.__class__.__name__} initialized with API key: {api_key}")

    def set_query_params(self, endpoint: str = 'all', **kwargs) -> None:
        """
        Specify the query parameters for fetching data. 
        
        :param endpoint: The API endpoint to fetch data from.
            - 'headlines' : Get the latest headlines by category.
            - 'top'       : Find live and historical top stories around the world. 
            - 'all'       : Find all live and historical articles.
            - 'similar'   : Find similar stories to a specific article based on its UUID.
            - 'uuid'      : Find specific articles by the UUID.
            - 'sources'   : Find sources to use in your news API requests.
        :param **kwargs: The query parameters to be passed. Visit `https://www.thenewsapi.com/documentation` 
                         for more information on query params for each endpoint.
        """
        # Check if kwargs is empty and assign default values.
        if not kwargs:
            self.params = {
                'api_token': self.api_key,
                'search': "crypto | cryptocurrency"
                 }   
        else:
            self.params = kwargs
            # Pass API key as query paramter.
            self.params['api_token']=self.api_key
         # Assign the input endpoint as an instance variable.
        if endpoint in ['headlines', 'top', 'all', 'similar', 'uuid', 'sources']:
            self.endpoint = endpoint
        else:
            raise ValueError(f"Invalid endpoint: {endpoint}")    
     
    def __process_data(self, response) -> pd.DataFrame:
        """
        Clean and store the JSON response in a DataFrame.
        
        :param response: JSON response of the API request.
        :return: Dataframe of the JSON response.
        """
        # Convert the JSON response into a dataframe.
        for article in response['data']:
            for column in ['title', 'description', 'snippet']:
                if article[column] is not None:
                    # Replace newline characters with space
                    article[column] = article[column].replace("\n", " ")
                    # Replace multiple spaces with a single space
                    article[column] = re.sub(r"\s+", " ", article[column])
                    # Strip leading and trailing spaces
                    article[column] = article[column].strip()
        df = pd.json_normalize(response['data'])
        # Convert dates to datetime objects.
        for column in ['published_at']:
            df[column] = pd.to_datetime(df[column])
            # Check if datetime objects are tz-aware; if not, localize to UTC before converting
            if df[column].dt.tz is None:
                df[column] = df[column].dt.tz_localize('UTC')
            df[column] = df[column].dt.tz_convert(None)
        return df

    def fetch_data(self, uuid: str=None) -> dict:
        """
        Fetches top news data from thenewsapi.com.
        
        :param uuid: UUID value if `endpoint = 'similar'` or `endpoint = 'uuid'`.
        :return: The JSON response from the API.
        """
        # Check if endpoint if 'uuid' or 'similar' and create the URL to fetch data.
        if self.endpoint in ['uuid', 'similar']:
            if uuid is not None: 
                url = self.base_url + self.endpoint + '/' + uuid
            else:
                raise ValueError("Enter Valid UUID.")
        else:
            url = self.base_url + self.endpoint        
        # Fetch data from the API with the passed parameters.
        try:
            response = requests.get(url=url, params=self.params)
            _LOG.debug(f"Fetching data from {response.request.url}")
            response.raise_for_status()
            _LOG.info("Data fetched successfully.")
            self.json_response = response.json()
        except requests.RequestException as e:
            _LOG.error(f"Error fetching data: {e}")
            raise
        df = self.__process_data(self.json_response)
        return df



# %% [markdown]
# ### sample data

# %%
datapipeline_3 = newsapiPipeline()
datapipeline_3.set_query_params()
df_newsapi = datapipeline_3.fetch_data()
df_newsapi.head()


# %% [markdown]
# ## marketaux.com pipeline

# %%
class marketauxPipeline:
    """
    Handles fetching data from the marketaux.com API.
    """
    def __init__(self, api_key: str = 'shRM7CyfkEGsBK83T3IB7YweAiKbzORMZjEWERtu'):
        """
        Intializes the pipeline.

        :param api_key: API key for authentication.
        """
        # Assign the passed API to an instance variable.
        self.api_key = api_key
        self.base_url = 'https://api.marketaux.com/v1/'
        _LOG.debug(f"{self.__class__.__name__} initialized with API key: {api_key}")

    def set_query_params(self, endpoint: str = 'news/all', **kwargs) -> None:
        """
        Specify the query parameters for fetching data. 
        
        :param endpoint: The API endpoint to fetch data from.
            - 'news/all'       : Find all live and historical articles.
            - 'news/similar'   : Find similar stories to a specific article based on its UUID.
            - 'news/uuid'      : Find specific articles by the UUID.
            - 'news/sources'   : Find sources to use in your news API requests.
            - 'entity/stats'   : Get an intraday view of how well entities performed over 
                                 different intervals using this endpoint.
            - 'entity/stats/aggregation'    : Returns an aggregation of entities for a single time frame, 
                                              rather than being broken down by date.
            - 'entity/trending/aggregation' : Use this endpoint to identify trending entities.
            - 'entity/search'               : Use this endpoint to search for all supported entities.
            - 'entity/type/list'            : Use this endpoint to return all supported entity types.
            - 'entity/industry/list'        : Use this endpoint to return all supported entity industries.
        :param **kwargs: The query parameters to be passed. Visit `https://www.marketaux.com/documentation` 
                         for more information on query params for each endpoint.
        """
        # Check if kwargs is empty and assign default values.
        if not kwargs:
            self.params = {
                'api_token': self.api_key,
                'search': "crypto | cryptocurrency"
                 }   
        else:
            self.params = kwargs
            # Pass API key as query paramter.
            self.params['api_token']=self.api_key
         # Assign the input endpoint as an instance variable.
        if endpoint in ['news/all', 'news/similar', 'news/uuid', 'news/sources', 'entity/stats', 
                        'entity/stats/aggregation', 'entity/tending/aggregation', 'entity/search'
                        'entity/type/list', 'entity/industry/list']:
            self.endpoint = endpoint
        else:
            raise ValueError(f"Invalid endpoint: {endpoint}")    
        
    def __process_data(self, response) -> pd.DataFrame:
        """
        Clean and store the JSON response in a DataFrame.
        
        :param response: JSON response of the API request.
        :return: Dataframe of the JSON response.
        """
        # Convert the JSON response into a dataframe.
        df = pd.json_normalize(response['data'])
        # Convert dates to datetime objects.
        for column in ['published_at']:
            df[column] = pd.to_datetime(df[column])
            # Check if datetime objects are tz-aware; if not, localize to UTC before converting.
            if df[column].dt.tz is None:
                df[column] = df[column].dt.tz_localize('UTC')
            df[column] = df[column].dt.tz_convert(None)
        # Unpack column values.
        for column in ['entities']:
            exploded_df = df.explode(column)
            df_list = []
            for idx, row in exploded_df.iterrows():
                # Check if the value is a dictionary and contains 'highlights'.
                if pd.notna(row[column]) and isinstance(row[column], dict) and 'highlights' in row[column]:
                    # Normalize the highlights columns.
                    highlights_df = pd.json_normalize(row[column], 'highlights')
                    # Create a copy of the row and normalize rest of the columns, except highlight.
                    row_data = row[column].copy()
                    del row_data['highlights']
                    row_df = pd.json_normalize(row_data)
                    # Process 'highlights'.
                    if not highlights_df.empty:
                        # Clean the text in highlights.
                        highlights_df['highlight'] = highlights_df['highlight'].str.replace("\n", " ", regex=True)
                        highlights_df['highlight'] = highlights_df['highlight'].str.replace('<.*?>', '', regex=True)
                        highlights_df['highlight'] = highlights_df['highlight'].str.replace(r"\s+", " ", regex=True)
                        highlights_df['highlight'] = highlights_df['highlight'].str.strip()
                        highlights_df = highlights_df.map(lambda x: f'"{x}"')
                        # Change column names to indicate hierarchy.
                        highlights_df.columns = ['highlights.' + col for col in highlights_df.columns]
                        # Combine the row values into a single list for each column.
                        highlights_df = {col: [highlights_df[col].tolist()] for col in highlights_df}
                        highlights_df = pd.DataFrame(highlights_df)
                        # Merge the `row_df` and `highlights_df` to form a complete row.
                        row_df = pd.concat([row_df]*len(highlights_df), ignore_index=True)
                    else:
                        highlights_df = pd.DataFrame(index=[0])
                    combined_df = pd.concat([row_df, highlights_df], axis=1)
                elif pd.notna(row[column]):
                    # Normalize non-dictionary values.
                    combined_df = pd.json_normalize(row[column] if isinstance(row[column], dict) else {})
                else:
                    # Handle NaN or None.
                    combined_df = pd.DataFrame(index=[0])
                combined_df.index = [idx] * len(combined_df)
                df_list.append(combined_df)
            # Combine all the rows into a single dataframe.
            normalized_df = pd.concat(df_list)
            normalized_df = normalized_df.map(lambda x: f'"{x}"' if isinstance(x, str) else x)
            # Group by index and aggregate lists.
            aggregated = normalized_df.groupby(by=normalized_df.index).agg(list)
            # Change column name to highlight hierarchy.
            aggregated.columns = [column + "." + col for col in aggregated.columns]
            df = df.drop(column, axis=1)
            df = df.join(aggregated)
        # Cleaning data.
        for column in ['title', 'description', 'snippet']:
            if df[column] is not None:
                # Replace newline characters with space.
                df[column] = df[column].replace("\n", " ")
                # Replace multiple spaces with a single space.
                df[column] = df[column].replace(r"\s+", " ", regex=True)
                df[column] = df[column].str.replace('<.*?>', '', regex=True)
                # Strip leading and trailing spaces.
                df[column] = df[column].str.strip()
        return df 
        
    def fetch_data(self, uuid: str=None) -> pd.DataFrame:
        """
        Fetches top news data from marketaux.com.
        
        :param uuid: UUID value if `endpoint = 'similar'` or `endpoint = 'uuid'`.
        :return: The JSON response from the API.
        """
        # Check if endpoint if 'uuid' or 'similar' and create the URL to fetch data.
        if self.endpoint in ['uuid', 'similar']:
            if uuid is not None: 
                url = self.base_url + self.endpoint + '/' + uuid
            else:
                raise ValueError("UUID is None.")
        else:
            url = self.base_url + self.endpoint        
        # Fetch data from the API with the passed parameters.
        try:
            response = requests.get(url=url, params=self.params)
            _LOG.debug(f"Fetching data from {response.request.url}")
            response.raise_for_status()
            _LOG.info("Data fetched successfully.")
            self.json_response = response.json()
        except requests.RequestException as e:
            _LOG.error(f"Error fetching data: {e}")
            raise
        df = self.__process_data(self.json_response)
        return df



# %% [markdown]
# ### sample data

# %%
datapipeline_4 = marketauxPipeline()
datapipeline_4.set_query_params()
df_marketaux = datapipeline_4.fetch_data()
df_marketaux.head()

# %%
