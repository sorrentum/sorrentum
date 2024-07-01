# Generate Fake Credit Card Transaction Data, Including Fraudulent Transactions

Note: Version v1.0 behavior has changed in such a way that it runs much faster, however transaction files are chunked, so that several files get generated per profile. If your downstream process expects 1 file per profile, please checkout the v0.5 release branch `release/v0.5`.

## General Usage

In this version, the general usage has changed:

Please run the datagen script as follow:

```bash
python datagen.py -n <NUMBER_OF_CUSTOMERS_TO_GENERATE> -o <OUTPUT_FOLDER> <START_DATE> <END_DATE>
```

To see the full list of options, use:

```bash
python datagen.py -h
```

You can pass additional options with the following flags:

- `-config <CONFIG_FILE>`: pass the name of the config file, defaults to `./profiles/main_config.json`
- `-seed <INT>`: pass a seed to the Faker class
- `-c <CUSTOMER_FILE>`: pass the path to an already generated customer file
- `-o <OUTPUT_FOLDER>`: folder to save files into

This version is modified from the version v0.5 to parallelize the work using `multiprocessing`, so as to take advantage of all available CPUs and bring a huge speed improvement.

Because of the way it parallelize the work (chunking transaction generation by chunking the customer list), there will be multiple transaction files generated per profile. Also not that if the number of customers is small, there may be empty files (i.e. files where no customer in the chunk matched the profile). This is expected.

With standard profiles, it was benchmarked as generating ~95MB/thread/min. With a 64 cores/128 threads AMD E3, I was able to generate 1.4TB of data, 4.5B transactions, in just under 2h, as opposed to days when running the previous versions.

The generation code is originally based on code by [Josh Plotkin](https://github.com/joshplotkin/data_generation). Change log of modifications to original code are below.

## Change Log

### v1.0

- Parallelized version, bringing orders of magnitude faster generation depending on the hardware used.

### v0.5

- 12x speed up thanks to some code refactoring.

### v0.4

- Only surface-level changes done in scripts so that simulation can be done using Python3
- Corrected bat files to generate transactions files.

### v0.3

- Completely re-worked profiles / segmentation of customers
- introduced fraudulent transactions
- introduced fraudulent profiles
- modification of transaction amount generation via Gamma distribution
- added 150k_ shell scripts for multi-threaded data generation (one python process for each segment launched in the background)

### v0.2

- Added unix time stamp for transactions for easier programamtic evaluation.
- Individual profiles modified so that there is more variation in the data.
- Modified random generation of age/gender. Original code did not appear to work correctly?
- Added batch files for windows users

### v0.1

- Transaction times are now included instead of just dates
- Profile specific spending windows (AM/PM with weighting of transaction times)
- Merchant names (specific to spending categories) are now included (along with code for generation)
- Travel probability is added, with profile specific options
- Travel max distances is added, per profile option
- Merchant location is randomized based on home location and profile travel probabilities
- Simulated transaction numbers via faker MD5 hash (replacing sequential 0..n numbering)
- Includes credit card number via faker
- improved cross-platform file path compatibility
