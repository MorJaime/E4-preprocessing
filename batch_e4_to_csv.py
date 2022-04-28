import os
import sys
import subprocess
import shutil
import argparse
from zipfile import ZipFile
import pandas as pd
import numpy as np

def make_parser():
    parser = argparse.ArgumentParser(
        description="Convert E4 zip file into multiple .csv files by device type"
    )
    # Add Arguments
    parser.add_argument('--path-to-raw', required=True,
                        help="A path to main folder containing raw data from required users, e.g.{G:\\User\\xxx\\open-pack\data\raw}")
    parser.add_argument('--path-output', required=True,
                        help="A path to main folder for output files, e.g.{G:\\User\\xxx\\open-pack\data\ADLTagger}")
    parser.add_argument('--path-to-shifts', required=True,
                        help="A path to device shift .csv file. {PATH\\wearable_shifts.csv}")
    parser.add_argument('--users', default = 'all',
                        help="list of Users to be extracted. {[U0101,U0102], all}")
    parser.add_argument('--devices', default = 'all',
                        help="list of devices to be extracted. {[e4-1,e4-2], all}")
    parser.add_argument('--sensors', default = 'all',
                        help="list of sensor type data to be extracted, {'acc','bvp','eda','temp'}.")
    parser.add_argument('--timezone', default='UTC',
                        help="Set timezone required for output data. {UTC, Japan}")
    parser.add_argument('--unit', default='g',
                        help="Acc unit to convert to, {g, m/s2}")
    return parser

def main():
    # Parse Command Line Argumenmts
    parser = make_parser()
    args = parser.parse_args()

    #Assign comand line arguments to variable
    main_folder = args.path_to_raw
    output_main = args.path_output
    shifts_path = args.path_to_shifts

    #Check user and device availability
    shifts_df = pd.read_csv(shifts_path)
    shifts_df['av_user'] = shifts_df.duplicated(['user'],keep='first')
    available_users = list(shifts_df[shifts_df['av_user']==False]['user'])

    if args.users == 'all':
        users_l = available_users
    else:
        users_l = args.users.split(',')

    if args.devices == 'all':
        devices_l = ['e4-1','e4-2']
    else:
        devices_l = args.devices.split(',')

    if args.sensors == 'all':
        sensors = 'acc,bvp,eda,temp'
    else:
        sensors = 'all'


    for user in users_l:
        if user not in available_users:
            sys.exit("User {} not available in shifts.csv file".format(user))

    for device in devices_l:
        if device not in ['e4-1','e4-2']:
            sys.exit("Device {} not valid".format(device))

    #Run e4_to_adl.py by user/device & session

    for user in users_l:

        sessions_l = list(shifts_df[shifts_df['user']==user]['session'])
        date = str(list(shifts_df[shifts_df['user']==user]['date'])[0])
        work_df = pd.DataFrame(shifts_df[shifts_df['user']==user])

        for device in devices_l:
            for session in sessions_l:
                path_to_zip = os.path.join(main_folder,date+'_'+user,device, session + '.zip')
                path_output_dir = os.path.join(output_main,user,device)
                shift = str(list(work_df[work_df['session']==session][device+'_shift'])[0])

                print("python e4_to_csv.py " + ("--path-to-zip "+path_to_zip) + (" --path-output-dir "+path_output_dir) + (" --sensors "+ sensors) +
                               (" --shift "+shift ) + (" --timezone "+args.timezone) + (" --unit "+ args.unit) )

                subprocess.run("python e4_to_csv.py " + ("--path-to-zip "+path_to_zip) + (" --path-output-dir "+path_output_dir) + (" --sensors "+ sensors) +
                               (" --shift "+shift ) + (" --timezone "+args.timezone) + (" --unit "+ args.unit) )

        
if __name__=='__main__':
    main()