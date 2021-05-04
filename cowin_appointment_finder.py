#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# API guide
# https://apisetu.gov.in/public/marketplace/api/cowin

from datetime import datetime, timedelta
import time

import logging
from logging.handlers import RotatingFileHandler

import sys
import os

import json
import requests

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import configparser

'''
Setup logging
'''
logger = logging.getLogger('cowin_appointment_finder')                                                              
logger.setLevel(logging.INFO)
log_filename = 'cowin_appointment_finder.log'

fhan = RotatingFileHandler(log_filename, maxBytes=1000000, backupCount=5)                                                                        
fhan.setLevel(logging.INFO)
formatter = logging.Formatter("[%(asctime)s] %(message)s")                           
fhan.setFormatter(formatter)
logger.addHandler(fhan)


## main entry point
def process():
    try:
        logger.info('#--START--#')
        t1 = time.perf_counter()
          
        #------Read config file
        config = configparser.RawConfigParser()
        config.read('setup.cfg')

        common_dict = dict(config.items('config'))
        logger.info(common_dict)
        days = int(common_dict['days_ahead'].strip())
        pincode_list = [x.strip() for x in common_dict['pincode_list'].split(',')]
        c_min_age_limit = int(common_dict['min_age_limit'].strip())
        c_fee = common_dict['fee'].strip()
        
        #starting from today
        sd = datetime.now()
        ed = datetime.now() + timedelta(days=days)
        
        sd_s = sd.strftime('%d-%m-%Y')
        ed_s = ed.strftime('%d-%m-%Y')
        #logger.info(sd_s)
        #logger.info(ed_s)
        logger.info(pincode_list)
        
        diff = int((ed - sd).days)        
        while (diff >= 0):
            sd_s = sd.strftime('%d-%m-%Y')
            logger.info('#############')
            
            # run for each pin code
            for p in pincode_list:
                logger.info('----------------------------')
                logger.info(f'date = {sd_s}, pin_code = {p}')                                        
                
                # https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=411037&date=05-05-2021
                
                ## construct url
                
                url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=' + p + '&date=' + sd_s
           
                logger.info(f'{url}')
                
                header = {'Accept-Language': 'hi_IN', 'accept': 'application/json'}
                
                res = requests.get(url, params={}, headers=header, verify=False)
                        
                res_list = json.loads(res.text)
                #logger.info(res_list)
                for s in res_list['sessions']:
                    # logger.info(f'{s}')
                    min_age_limit = s['min_age_limit']
                    fee = s['fee']
                    name = s['name']
                    available_capacity = int(s['available_capacity'])
                    vaccine = s['vaccine']
                    
                    if (min_age_limit == c_min_age_limit and fee == c_fee and available_capacity > 0):
                        logger.info(f'name = {name}, available_capacity = {available_capacity}, vaccine = {vaccine}, fee = {fee}, min_age_limit = {min_age_limit}')
                        
                logger.info('----------------------------')
                    
                
            
            sd = sd + timedelta(days=1)
            diff = int((ed - sd).days)
        
      
            
        t2 = time.perf_counter()
        logger.info(f'Time(s)= {t2 - t1:0.2f}')
        logger.info('#---END---#')
    except Exception as e:
        exception_msg = str(e)
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        
        logger.error(f'[ERROR] [fetcher] Exception type: {exception_type}, Exception: {exception_msg}, Line number: {line_number}')
        return



## main entry point
if __name__ == '__main__':
    try:
        process()
    except Exception as e:
        logger.error("[ERROR] [main] Exiting...")
        sys.exit(0)


