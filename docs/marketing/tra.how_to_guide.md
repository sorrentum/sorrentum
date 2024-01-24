# How to extract data from Tra

<!-- toc -->

- [Locations](#locations)
- [Dataflow](#dataflow)
  * [Input](#input)
  * [Output](#output)
- [Download Data](#download-data)
- [Usage](#usage)

<!-- tocstop -->

## Locations

- The module is located at `marketing/tra`
- Example notebooks are at:
  - `marketing/notebooks/SorrTask601_Extract_people_from_Tra_company_html.ipynb`
  - `marketing/notebooks/SorrTask601_Extract_VCs_from_Tra_search_mhtml.ipynb`

## Dataflow

### Input

- An MIME HTML file containing:
  1. A table of VC company names
  2. A list of investors from the company

### Output

- According to the input type, output can be:
  1. A pandas dataframe containing the VC names and its information
  2. A pandas dataframe containing the investors' `First Name`, `Last Name` and
     their linkedin profiles link

## Download Data

- We want to use only static data as the source of our extraction code. To
  download the data page:
  1. In any modern browser, open a page containing required data
  2. Use the browser's `Save As` button to download the webpage as a
     `Web page, single file`. Or use any other download method that can fulfill
     the requirement in step 3
  3. If you see the downloaded file format is `.mht` or `.mhtml`, you can
     process forward. Otherwise you won't be able to bypass the check layer from
     the website
  4. Save the `.mhtml` file and its path will work as input data

## Usage

- Import the module using `import marketing.tra as mrktra`
- Each file in this module only have one public function. It takes the
  downloaded MIME HTML (`.mhtml`) file path as parameter and returns a pandas
  dataframe containing the extracted data.
- In any notebook, run the following script to get a pandas dataframe
  representing the data:

  ```python
  import marketing.tra as mrktra

  # For VC extraction:
  VCs_mhtml_path = "<VCs_mthml_file_path>"
  VCs_dataframe = mrktra.get_VCs_from_mhtml(VC_mhtml_path)
  # For employee list extraction:
  employees_html_path = "<employees_html_path>"
  employees_dataframe = mrktra.get_employees_from_mhtml(employees_html_path)

  ```
