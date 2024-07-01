import pathlib
import random
import sys
from datetime import timedelta, datetime
from faker import Faker
import argparse
from profile_weights import Profile
import json
import csv

from datagen_customer import headers


fake = Faker()
transaction_headers = [
    'trans_num', 
    'trans_date', 
    'trans_time',
    'unix_time', 
    'category', 
    'amt', 
    'is_fraud', 
    'merchant', 
    'merch_lat', 
    'merch_long'
]

# read this only once / built a map of merchant per category for easy lookup
merchants = {}
with open('data/merchants.csv', 'r') as merchants_file:
    csv_reader = csv.reader(merchants_file, delimiter='|')
    # skip header
    csv_reader.__next__()
    for row in csv_reader:
        if merchants.get(row[0]) is None:
            merchants[row[0]] = []
        merchants[row[0]].append(row[1])


class Customer:
    def __init__(self, raw):
        self.raw = raw.strip().split('|')
        self.attrs = self.parse_customer(raw)
        self.fraud_dates = []

    def print_trans(self, trans, is_fraud, fraud_dates):
        is_traveling = trans[1]
        travel_max = trans[2]

        for t in trans[0]:
            ## Get transaction location details to generate appropriate merchant record
            merchants_in_category = merchants.get(t[4]) # merchant category
            chosen_merchant = random.sample(merchants_in_category, 1)[0]

            cust_lat = self.attrs['lat']
            cust_long = self.attrs['long']

            # not traveling, so use 1 decimial degree (~70mile) radius around home address
            rad = 1
            if is_traveling:
                # hacky math.. assuming ~70 miles per 1 decimal degree of lat/long
                # sorry for being American, you're on your own for kilometers.
                rad = (float(travel_max) / 100) * 1.43

            # geo_coordinate() uses uniform distribution with lower = (center-rad), upper = (center+rad)
            merch_lat = fake.coordinate(center=float(cust_lat),radius=rad)
            merch_long = fake.coordinate(center=float(cust_long),radius=rad)

            if (is_fraud == 0 and t[1] not in fraud_dates) or is_fraud == 1:
                features = self.raw + t + [chosen_merchant, str(merch_lat), str(merch_long)]
                print("|".join(features))


    def parse_customer(self, line):
        # separate into a list of attrs
        cols = [c for c in line.strip().split('|')]
        # create a dict of name: value for each column
        return dict(zip(headers, cols))

def valid_date(s):
    try:
        return datetime.strptime(s, "%m-%d-%Y")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


def main(customer_file, profile_file, start_date, end_date, out_path=None, start_offset=0, end_offset=sys.maxsize):

    profile_name = profile_file.name
    profile_file_fraud = pathlib.Path(*list(profile_file.parts)[:-1] + [f"fraud_{profile_name}"])

    # setup output to file by redirecting stdout
    original_sys_stdout = sys.stdout
    if out_path is not None:
        f_out = open(out_path, 'w')
        sys.stdout = f_out

    with open(profile_file, 'r') as f:
        profile_obj = json.load(f)
    with open(profile_file_fraud, 'r') as f:
        profile_fraud_obj = json.load(f)

    profile = Profile({**profile_obj})
    profile.set_date_range(start_date, end_date)
    fraud_profile = Profile({**profile_fraud_obj})

    inter_val = (end_date - start_date).days - 7
    # for each customer, if the customer fits this profile
    # generate appropriate number of transactions
    with open(customer_file, 'r') as f:
        f.readline()
        print("|".join(headers + transaction_headers))
        line_num = 0
        fail = False
        # skip lines out of range
        while line_num < start_offset:
            try:
                f.readline()
                line_num += 1
            except EOFError:
                # end of file?
                fail = True
                break
        if not fail:
            for row in f.readlines():
                cust = Customer(row)
                if cust.attrs['profile'] == profile_name:
                    is_fraud = 0
                    fraud_flag = random.randint(0,100) # set fraud flag here, as we either gen real or fraud, not both for
                                            # the same day.
                    fraud_dates = []
                    # decide if we generate fraud or not
                    if fraud_flag < 99: #11->25
                        fraud_interval = random.randint(1,1) #7->1
                        # rand_interval is the random no of days to be added to start date
                        rand_interval = random.randint(1, inter_val)
                        #random start date is selected
                        newstart = start_date + timedelta(days=rand_interval)
                        # based on the fraud interval , random enddate is selected
                        newend = newstart + timedelta(days=fraud_interval)
                        # we assume that the fraud window can be between 1 to 7 days #7->1
                        fraud_profile.set_date_range(newstart, newend)
                        is_fraud = 1
                        temp_tx_data = fraud_profile.sample_from(is_fraud)
                        fraud_dates = temp_tx_data[3]
                        cust.print_trans(temp_tx_data, is_fraud, fraud_dates)

                    # we're done with fraud (or didn't do it) but still need regular transactions
                    # we pass through our previously selected fraud dates (if any) to filter them
                    # out of regular transactions
                    
                    is_fraud = 0
                    temp_tx_data = profile.sample_from(is_fraud)
                    cust.print_trans(temp_tx_data, is_fraud, fraud_dates)
                line_num += 1
                if line_num > end_offset:
                    break

    if out_path is not None:
        sys.stdout = original_sys_stdout


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Transaction Generator')
    parser.add_argument('customer_file', type=pathlib.Path, help='Customer file generated with the datagen_customer script')
    parser.add_argument('profile', type=pathlib.Path, help='profile')
    parser.add_argument('start_date', type=valid_date, help='Transactions start date')
    parser.add_argument('end_date', type=valid_date, help='Transactions start date')
    parser.add_argument('-o', '--output', type=pathlib.Path, help='Output file path')

    args = parser.parse_args()

    customer_file = args.customer_file
    profile_file = args.profile 
    start_date = args.start_date
    end_date = args.end_date
    out_path = args.output

    main(customer_file, profile_file, start_date, end_date, out_path)

    
