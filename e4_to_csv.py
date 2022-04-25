import os
import argparse
import shutil
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
    parser.add_argument('--sensors', required=True,
                        help="list[sens1,sens2,etc.]sensor data to be extracted, {'acc','bvp','eda','temp'}.")
    parser.add_argument('--shift', required=True,
                        help="Milli second to shift csv's timestamp")
    parser.add_argument('--timezone', default='UTC',
                        help="Set timezone required for output data. {UTC,Japan}")
    parser.add_argument('--unit', default='g',
                        help="Acc unit to convert to, {g, m/s2}")
    return parser


#path_to_zip = r'G:/JaimeMorales/Codes/openlogi/20220301_U0201/e4-1/S0200.zip'
#output_dir= r'G:/JaimeMorales/Codes/openlogi/20220301_U0201/e4-1'
#acc_unit = 'g'
#shift = 200
#sensors = []

def setup_dir(path):
    """ Clean

    Args.
    ------
    - pathr: path
    """
    if not os.path.isdir(path):
        # If selected DIR does not exist, create it.
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
    df['time'] = timestamps
    
    
    time_1 = np.array(df['time'])
    time_ms, time = np.modf(time_1)
    df['time'] = time
    if tz=='UTC':
        utc=True
    else:
        utc=False
    df['time'] = pd.to_datetime(df['time'], yearfirst=True, utc=utc, unit='s')
    if tz!='UTC':
        df['time'] = df['time'].dt.tz_localize('UTC').dt.tz_convert(tz)
    df['time_ms'] = np.round(time_ms, 3)
    
    #print(df['time_ms'])
    columns = df.columns.to_list()
    columns = columns[-2:] + columns[:-2]
    
    df = df[columns]
    
    return df

def set_unit(inn_df,unit):
    
    x = np.array(inn_df['acc_x'])
    y = np.array(inn_df['acc_y'])
    z = np.array(inn_df['acc_z'])
    
    if unit == 'm/s2':
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

def save_file(df,output_dir,sensor,sess_id):
    
    writedir = os.path.join(output_dir,sensor)
    setup_dir(writedir)
    writepath = os.path.join(writedir, sess_id)
    df.to_csv(writepath,index=False)
    print(writepath)
    
    return

def main():
    # Parse Command Line Argumenmts
    parser = make_parser()
    args = parser.parse_args()
    
    path_to_zip = str(args.path_to_zip)

    inter_dir = '/'.join(path_to_zip.split('\\')[:-1])
    inter_dir = os.path.join(inter_dir,'interim')
    sess_id = path_to_zip.split('\\')[-1:][0].replace('.zip','.csv')

    with ZipFile(path_to_zip, 'r') as zipObj:
        setup_dir(inter_dir)
        # Extract all the contents of zip file in different directory
        zipObj.extractall(inter_dir)
        
    sensors = args.sensors.split(',')
    print(sensors)

    for sensor in sensors:
    
        df = load_sensor_data(inter_dir,sensor.upper()+'.csv',float(args.shift),tz = str(args.timezone))
    
        if sensor == 'acc':
            df = set_unit(df,str(args.unit))
        
        save_file(df,str(args.path_output_dir),sensor,sess_id)

    shutil.rmtree(inter_dir)

        
if __name__=='__main__':
    main()