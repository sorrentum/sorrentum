"""
Implementation of DB interface for the ETL and QA pipeline.

Import as:
import sorrentum_sandbox.projects.Issue22_Team3_Implement_sandbox_for_Coinmarketcap.db.py as ssan_cmc_db
"""

from typing import Optional

import pandas as pd
import pymongo

import helpers.hdbg as hdbg
import sorrentum_sandbox.common.client as ssanclie
import sorrentum_sandbox.common.download as ssandown
import sorrentum_sandbox.common.save as ssansave

# #############################################################################
# MongoDataSaver
# #############################################################################

class MongoDataSaver(ssansave.DataSaver):
    """
    Store data to MongoDB.
    """

    def __init__(self, mongo_client: pymongo.MongoClient, db_name: str):
        self.mongo_client = mongo_client
        self.db_name = db_name

    def save(self, data: ssandown.RawData, collection_name: str) -> None:
        data = data.get_data()
        if isinstance(data, pd.DataFrame):
            data = data.to_dict("records")
        # else:
        #     hdbg.dassert_isinstance(data, list, "This data type is not supported")
        db = self.mongo_client
        db[self.db_name][collection_name].insert_one(data)

    def save_many(self, data: ssandown.RawData, collection_name: str) -> None:
        data = data.get_data()
        if isinstance(data, pd.DataFrame):
            data = data.to_dict("records")
        # else:
        #     hdbg.dassert_isinstance(data, list, "This data type is not supported")
        db = self.mongo_client
        db[self.db_name][collection_name].insert_many(data)

# #############################################################################
# MongoClient Data Loader
# #############################################################################


class MongoClient(ssanclie.DataClient):
    """
    Load CoinMarketCap data located in MongoDB into the memory.
    """

    def __init__(self, mongo_client: pymongo.MongoClient, db_name: str):
        """
        Build CoinMarketCap MongoDB client.

        :param mongo_client: MongoDB client
        :param db_name: name of the database to connect to
        """
        self.mongo_client = mongo_client
        self.db_name = db_name

    def load(
        self,
        collection_name: str,
        *,
        start: Optional[int]= None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Load data from MongoDB collection directory.

        :param collection_name: collection name where data come from
        :return: loaded data
        """
        # Access the data.
        db = self.mongo_client[self.db_name]
        data = list(db[collection_name].find())
        # Convert the data to a dataframe.
        df = pd.DataFrame(data)
        return df