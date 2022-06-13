import os
import sys
import shutil
import argparse
from zipfile import ZipFile
import pandas as pd
import numpy as np

def make_parser():
    parser = argparse.ArgumentParser(
        description="Convert E4 zip file into multiple .csv files by sensor type"
    )
    # Add Arguments
    parser.add_argument('--path-to-zip', required=True,
                        help="A path to an input session zip file.")
    parser.add_argument('--path-output-dir', required=True,
                        help="A path to an output folder for selected sensors")
    parser.add_argument('--shift', required=True,
                        help="Milli second to shift csv's timestamp")
    parser.add_argument('--timezone', default='UTC',
                        help="Set timezone required for output data. {UTC,Japan}")
    parser.add_argument('--unit', default='g',
                        help="Acc unit to convert to, {g, m/s2}")
    return parser

def setup_dir(path):
    """ Clean

    Args.
    ------
    - pathr: path
    """
    if not os.path.isdir(path):
        # If selected DIR does not exist, create it.
        #print(path)
        os.makedirs(path)
        if os.path.isdir(path):
            print(">> Done: create directory [{}]".format(path))
    return path

def load_sensor_data(readir,file,shift=0,tz='UTC'):
    
    path=os.path.join(readir,file)
    df=pd.read_csv(path)
    
    file = file.replace('.csv','')
    file = file.lower()
    
    if file == 'acc':
        cols = [file+'_x',file+'_y',file+'_z']
    else:
        cols = [file]
        
    start_time = float(df.columns[0])+(shift/1000)
    df.set_axis(cols,axis=1,inplace=True)
    
    
    freq = 1/df[df.columns[0]][0]
    df.drop(0,axis=0,inplace=True)
    timestamps = np.linspace(0,freq*len(df),num = len(df))+start_time
    df['timestamp'] = timestamps

    if tz=='UTC':
        utc=True
    else:
        utc=False
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=utc, yearfirst=True, unit='s')

    if tz!='UTC':
        df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(tz)

    df["time"], df["time_milli"] = df["timestamp"].dt.strftime('%Y%m%d_%H:%M:%S.'), df["timestamp"].dt.microsecond // 1000
    df["time"] = df["time"].astype(str) + df["time_milli"].astype(str).str.zfill(3)
    df["group"] = df["timestamp"].dt.strftime('%Y%m%d_%H%M')
    
    return df

def set_unit(inn_df,acc_unit):
    
    x = np.array(inn_df['acc_x'])
    y = np.array(inn_df['acc_y'])
    z = np.array(inn_df['acc_z'])
    
    if acc_unit == 'm/s2':
        x = x * 9.80665 / 64
        y = y * 9.80665 / 64
        z = z * 9.80665 / 64
    else:
        x = x / 64
        y = y / 64
        z = z / 64
    
    new_df = inn_df
    new_df['acc_x'] = x
    new_df['acc_y'] = y
    new_df['acc_z'] = z
    
    return new_df

def write_csv(df, path_output_dir, sess_id):
    
    groups = df["group"].drop_duplicates().reset_index(drop=True)
    # Clean ouput directory

    setup_dir(path_output_dir)
        
    for group in groups:
        df_selected = df[df["group"] == group].sort_values(by=["timestamp"])
        out_path = "/".join(path_output_dir.split("/")[:-1])
        s_type = str(path_output_dir.split("/")[-1])
        target_path = setup_dir(os.path.join(out_path, "acc2",s_type,sess_id))
        target_file_name = group+"00_acc2.csv"
        filename = os.path.join(target_path, target_file_name)
        #print(df_selected[["time", "acc_x", "acc_y", "acc_z"]])
        df_selected[["time", "acc_x", "acc_y", "acc_z"]].to_csv(filename, index=False, header=["time", "x", "y", "z"])
        print(">> Done: write [Acc ] =>{}".format(filename))
        
    return len(groups)

def main():
    # Parse Command Line Argumenmts
    parser = make_parser()
    args = parser.parse_args()
    
    path_to_zip = str(args.path_to_zip)
    output_dir = str(args.path_output_dir)

    inter_dir = "/".join(output_dir.split("/")[:-1])
    inter_dir = os.path.join(inter_dir,'interim')
    #print('inter_dir',inter_dir)
    sess_id = path_to_zip.split("/")[-1:][0].replace('.zip','')


    with ZipFile(path_to_zip, 'r') as zipObj:
        setup_dir(inter_dir)
        # Extract all the contents of zip file in different directory
        zipObj.extractall(inter_dir)
        
    df = load_sensor_data(inter_dir,'ACC.csv',float(args.shift),args.timezone)
    df = set_unit(df,args.unit)
    write_csv(df, args.path_output_dir,sess_id)

        
if __name__=='__main__':
    main()