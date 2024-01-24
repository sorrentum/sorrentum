# How to extract data from DropContact

<!-- toc -->

- [Locations](#locations)
- [Dataflow](#dataflow)
  * [Input](#input)
  * [Output](#output)
- [Usage](#usage)

<!-- tocstop -->

## Locations

- The module is located at `marketing/dropcontact`
- An example notebook is at
  `marketing/notebooks/SorrTask606_Get_email_from_dropcontact.ipynb`
- It contains a full process for extracting data using `DropContact` API and
  adding into an existing Google sheet

## Dataflow

### Input

- Three sequences representing `First Name`, `Last Name`, `Company Name`
- API key for dropcontact

### Output

- DataFrame containing all data available from DropContact API
- Empty string is set for data not present

## Usage

- Import the module using `import marketing.dropcontact as mrkdrop`
- The module provides a single function for extraction of data for `DropContact`
  API
- It takes three Sequence of data (can be python list, pandas column, etc.) and
  an API key for dropcontact
- The processing time is ~50 investors per minute
- In any notebook, run the following script to get a pandas dataframe
  representing the data returned from DropContact:

  ```python
  import marketing.dropcontact as mrkdrop

  API_KEY = <DropContact_API_KEY>
  first_names = <First Name Sequence>
  last_names = <Last Name Sequence>
  company_names = <Company Name Sequence>
  dropcontact_dataframe = mrkdrop.get_email_from_dropcontact(first_names, last_names, company_names, API_KEY)

  ```
