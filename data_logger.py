#!usr/bin/python

import sys
import os
import time
import argparse
from ADS1256_definitions import *
from pipyadc import ADS1256


def logger(channels, outfile, rate=1, n_digits=3, mode='s'):
    
    # get instance of ADC Board
    adc = ADS1256()
    
    # self-calibration
    adc.cal_self()

    # channels
    _all_channels = [POS_AIN0, POS_AIN1,
                     POS_AIN2, POS_AIN3,
                     POS_AIN4, POS_AIN5,
                     POS_AIN6, POS_AIN7]
    # gnd
    _gnd = NEG_AINCOM

    # get actual channels by name
    if len(channels) > 8 and mode == 's':
        raise ValueError('Only 8 single-ended input channels exist')
    elif len(channels) > 4 and mode == 'd':
        raise ValueError>('Only 4 differential input channels exist')
    else:
        if mode == 's':
            actual_channels = [_all_channels[i]|_gnd for i in range(len(channels))]
        elif mode == 'd':
            actual_channels = [_all_channels[i]|_all_channels[i+1] for i in range(len(channels))]
        else:
            raise ValueError('Unknown measurement mode %s. Supported modes are "d" for differential and "s" for single-ended measurements.' % mode)

    # open outfile
    with  open(outfile, 'w') as out:
        
        # write info header
        out.write('# Date: %s \n' % time.asctime())
        out.write('# Measurement in %s mode.\n' % ('differential' if mode == 'd' else 'single-ended'))
        out.write('# ' + ' \t'.join(channels) + '\n')

        # try -except clause for ending logger
        try:
            print 'Start logging channels %s to file %s.\nPress CTRL + C to stop.' % (', '.join(channels), outfile)
            while True:

                start = time.time()
                
                # get current channels 
                raw = adc.read_sequence(actual_channels)
                volts = [b * adc.v_per_digit for b in raw]
                 
                end = time.time()

                # write voltages to file
                out.write('\t'.join('%.{}f'.format(n_digits) % v for v in volts)+ '\n')

                # wait
                time.sleep(1./rate)

                # actual logging and readout rate
                logging_rate =  1. / (time.time() - start)
                readout_rate = 1. / (end - start)

        except KeyboardInterrupt:
            print '\nStopping logger...'
    
    print 'Finished'

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--channels', help='Channel names', required=True)
    parser.add_argument('-o', '--outfile', help='Output file', required=True)
    parser.add_argument('-r', '--rate', help='Timeout between loggings', required=False)
    parser.add_argument('-d', '--digits', help='Digits for logged data', required=False)
    parser.add_argument('-m', '--mode', help='d for differential or s for single-ended mode', required=False)
    args = vars(parser.parse_args())

    channels = args['channels'].split(' ')  #['SEM_1_OBEN', 'SEM_1_UNTEN']
    outfile = args['outfile']  #'./calibrations/calibration_0.txt'
    rate = 1 if 'rate' not in args else float(args['rate'])
    n_digits = 3 if 'digits' not in args else int(args['digits'])
    mode = 's' if 'mode' not in args else args['mode']

    # start logger
    logger(channels=channels, outfile=outfile, rate=rate, n_digits=n_digits, mode=mode)
