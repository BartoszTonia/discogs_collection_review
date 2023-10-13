from discogs_client.exceptions import HTTPError
from lib.mail_notification import report
from release_object import ReleaseObject
from lib.credentials import Credentials
from datetime import datetime
from pathlib import Path
from csv import writer
from time import time
import pandas as pd
import discogs_client
import argparse


credentials = Credentials()


def args_parser():
    description = "Review most valuable records in Discogs collection"
    token_h = "Paste your developer token (get your token at https://www.discogs.com/settings/developers)"
    user_h = "User name"
    mail_h = "Mail recipient of the pricelist"

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-t', '--token', dest="token", type=str, help=token_h)
    parser.add_argument('-u', '--user', dest="user", type=str, help=user_h)
    parser.add_argument('-m', '--mail', dest="mail", type=str, help=mail_h)

    args = parser.parse_args()
    token = args.token
    user = args.user
    mail = args.mail

    if args.token is None:
        token = credentials.token

    if args.user is None:
        user = credentials.user

    if args.mail is None:
        mail = credentials.mail_in

    return user, token, mail


user, developer_token, mail_in = args_parser()


def get_releases():
    try:
        discogs_cl = discogs_client.Client("PricelistDiscogs/0.9.1", user_token=developer_token)
        return discogs_cl.user(user).collection_folders[0]
    except HTTPError:
        print('paste your user/token in arguments or edit "lib/credentials.py"')
        quit()


releases = get_releases()
# releases = [864431, 1074649]

csv_headers = 'id,title,for_sale,start,low,med,high,avg_rating,rating_count,want,have,last_sold,styles,' \
              'year_of_release,date_of_scrape,release_url,label,catalog,format\n'


def get_or_create_csv_path(label):
    """
    Creates and returns the output CSV file path with the given label name.
    If the file already exists, returns its path directly.

    Args:
        label: A string representing the label name for the output CSV file.

    Returns:
        A Path object representing the path to the output CSV file.
    """
    out_csv_path = Path(f'out/{label}.csv')
    if out_csv_path.exists():
        return out_csv_path
    else:
        out_csv_path.parent.mkdir(parents=True, exist_ok=True)
        out_csv_path.touch()
        out_csv_path.write_text(csv_headers)
        return out_csv_path


temp_path = get_or_create_csv_path(f'collection_{user}')
temp_df = pd.read_csv(temp_path, encoding='utf-8')


def create_db( temp, location ):
    try:
        df = pd.read_csv(temp, encoding='utf-8')
        print(len(df))
        df = df[~((df['format'].isnull()) & (df['label'].isnull()))]
        df.to_csv(temp, index=False)
        df.to_csv(location, index=False)
        print('File was successfully created -- {}'.format(location))
    except ValueError:
        print("Empty file, not created -- {}".format(location), ValueError)
        pass

try:
    for each in releases.releases:
        if each.id in temp_df['id'].values:
            print('duplicate')
            pass
        else:
            release_object = ReleaseObject(each.release.id, each.release.title)
            print(release_object.csv_object())
            row = release_object.csv_object()
            with temp_path.open('a', newline='', encoding='utf-8') as temp:
                csv_writer = writer(temp)
                csv_writer.writerow(row)
except KeyboardInterrupt:
    print('Ctrl+C...')
    quit()


t = time()
timestamp = datetime.fromtimestamp(t).strftime('_%Y%m%d_%H_%M_%S')
out_path = Path(f'out/{temp_path.stem}_{timestamp}.csv')
create_db(temp_path, out_path)
if out_path.exists():
    temp_path.unlink()
report(credentials.mail_out, credentials.mail_pass, mail_in, out_path)
