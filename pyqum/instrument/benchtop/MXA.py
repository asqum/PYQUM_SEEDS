#!/usr/bin/env python
'''Communicating with Benchtop RIGOL Spectrum Analyzer RSA5065-TG
'''

from colorama import init, Fore, Back
init(autoreset=True) #to convert termcolor to wins color

from os.path import basename as bs
mdlname = bs(__file__).split('.')[0] # module's name e.g. PSG

from time import sleep

import visa
from pyqum.instrument.logger import address, set_status, status_code, debug
from pyqum.instrument.logger import translate_scpi as Attribute

debugger = debug(mdlname)

# INITIALIZATION
def Initiate():
    ad = address()
    rs = ad.lookup(mdlname) # Instrument's Address
    rm = visa.ResourceManager()
    try:
        bench = rm.open_resource(rs) #establishing connection using GPIB# with the machine
        stat = bench.write('*CLS') #Clear buffer memory
        bench.write(':SYSTem:PRESet') #Mode preset
        bench.read_termination = '\n' #omit termination tag from output 
        bench.timeout = 150000 #set timeout in ms
        bench.write(":INIT:CONT ON") #continuous mode
        sleep(3)
        set_status(mdlname, dict(state='connected'))
        print(Fore.GREEN + "%s's connection Initialized: %s" % (mdlname, str(stat[1])[-7:]))
    except: 
        set_status(mdlname, dict(state='DISCONNECTED'))
        print(Fore.RED + "%s's connection NOT FOUND" % mdlname)
        bench = "disconnected"
    return bench

@Attribute
def model(bench, action=['Get', '']):
    SCPIcore = '*IDN'  #inquiring machine identity: "who r u?"
    return mdlname, bench, SCPIcore, action
@Attribute
def frequency(bench, action=['Get', '']):
    '''This command sets the signal generator output frequency for the CW frequency mode, or increments or decrements the current RF frequency setting.\n
        action=['Set','5GHz']'''
    SCPIcore = ':FREQ:CENT'
    return mdlname, bench, SCPIcore, action
@Attribute
def fspan(bench, action=['Get', '']):
    '''This command sets the signal generator output frequency for the CW frequency mode, or increments or decrements the current RF frequency setting.\n
        action=['Set','150MHz']'''
    SCPIcore = ':FREQ:SPAN'
    return mdlname, bench, SCPIcore, action
@Attribute
def rbw(bench, action=['Get', '']):
    '''This command sets the signal generator output frequency for the CW frequency mode, or increments or decrements the current RF frequency setting.\n
        action=['Set','1MHz']'''
    SCPIcore = ':BANDwidth:RESolution'
    return mdlname, bench, SCPIcore, action
@Attribute
def vbw(bench, action=['Get', '']):
    '''This command sets the signal generator output frequency for the CW frequency mode, or increments or decrements the current RF frequency setting.\n
        action=['Set','100kHz']'''
    SCPIcore = ':BANDwidth:VIDeo'
    return mdlname, bench, SCPIcore, action
@Attribute
def trigger_source(bench, action=['Get', '']):
    '''Trigger Source:\n
        EXTernal1| EXTernal2| IMMediate| LEVel| FMT|LINE| FRAMe| RFBurst| PERiod| FMT| VIDeo| IF| TV 
        action=['Set','EXTernal1']'''
    SCPIcore = ':TRIGger:SOURCe'
    return mdlname, bench, SCPIcore, action
@Attribute
def preamp(bench, action=['Get', '']):
    '''Pre-amplifier state.\n
        action=['Set','ON']'''
    SCPIcore = ':POW:GAIN'
    return mdlname, bench, SCPIcore, action
@Attribute
def preamp_band(bench, action=['Get', '']):
    '''Pre-amplifier bandwidth.\n
        action=['Set','FULL']'''
    SCPIcore = ':POW:GAIN:BAND'
    return mdlname, bench, SCPIcore, action
@Attribute
def attenuation(bench, action=['Get', '']):
    '''Attenuation.\n
        action=['Set','0dB']'''
    SCPIcore = ':POW:ATT'
    return mdlname, bench, SCPIcore, action
@Attribute
def attenuation_auto(bench, action=['Get', '']):
    '''Auto Attenuation mode.\n
        action=['Set','ON']'''
    SCPIcore = ':POW:ATT:AUTO'
    return mdlname, bench, SCPIcore, action

def fpower(bench, freq):
    # sleep(0.3)
    bench.query('*OPC?')
    bench.write(":CALC:MARK1:MODE POS")
    bench.write(":CALC:MARK1:X %s" %freq)
    return bench.query(":CALCulate:MARKer1:Y?")


def close(bench, reset=True):
    if reset:
        bench.write('*RST') # reset to factory setting (including switch-off)
        set_status(mdlname, dict(config='reset'))
    else: set_status(mdlname, dict(config='previous'))
    try:
        bench.close() #None means Success?
        status = "Success"
    except: status = "Error"
    set_status(mdlname, dict(state='disconnected'))
    print(Back.WHITE + Fore.BLACK + "%s's connection Closed" %(mdlname))
    return status
        

# Test Zone
def test(detail=True):
    S={}
    S['x'] = Initiate()
    s = S['x']
    if s is "disconnected":
        pass
    else:
        if debug(mdlname, detail):
            print(Fore.RED + "Detailed Test:")
            # print('SCPI TEST:')
            # s.write("*SAV 00,1")
            model(s)
            frequency(s)
            frequency(s, action=['Set','5.5GHz'])
            fspan(s)
            fspan(s, action=['Set','150MHz'])
            preamp(s, action=['Set','ON'])
            preamp_band(s, action=['Set','FULL'])
            attenuation(s, action=['Set','0dB'])
            attenuation_auto(s, action=['Set','ON'])
            print('Power at 5.5GHz is %s' %fpower(s, '5.5GHz'))
            
        else: print(Fore.RED + "Basic IO Test")
    if not bool(input("Press ENTER (OTHER KEY) to (skip) reset: ")):
        state = True
    else: state = False
    close(s, reset=state)
    return

