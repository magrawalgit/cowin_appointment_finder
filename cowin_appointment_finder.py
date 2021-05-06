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
import argparse
import copy
from hashlib import sha256


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


def get_beneficiaries(request_header):
    beneficiaries = requests.get("https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries", headers=request_header)

    if beneficiaries.status_code == 200:
        beneficiaries = beneficiaries.json()['beneficiaries']

        refined_beneficiaries = []
        for beneficiary in beneficiaries:
            beneficiary['age'] = datetime.today().year - int(beneficiary['birth_year'])

            tmp = {
                'beneficiary_reference_id': beneficiary['beneficiary_reference_id'],
                'name': beneficiary['name'],
                'vaccine': beneficiary['vaccine'],
                'age': beneficiary['age'],
                'status': beneficiary['vaccination_status']
            }
            refined_beneficiaries.append(tmp)

        print(refined_beneficiaries)

    else:
        print('Unable to fetch beneficiaries')
        print(beneficiaries.status_code)
        print(beneficiaries.text)
        os.system("pause")
        return []
        
def authenticate_using_otp(mobile, request_header):
    try:
        """
        This function generate OTP and returns a new token
        """
        data = {"mobile": mobile,
                "secret": "U2FsdGVkX1+b2/jGHLoV5kD4lpHdQ/CI7p3TnigA+6ukck6gSGrAR9aAuWeN/Nod9RrY4RaREfPITQfnqgCI6Q=="}
        print(f"Requesting OTP with mobile number {mobile}..")
        txnId = requests.post(url='https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP', json=data, headers=request_header)

        if txnId.status_code == 200:
            txnId = txnId.json()['txnId']
        else:
            print('Unable to Create OTP')
            print(txnId.text)
            os.system("pause")

        OTP = input("Enter OTP: ")
        data = {"otp": sha256(str(OTP).encode('utf-8')).hexdigest(), "txnId": txnId}
        print(f"Validating OTP...")

        token = requests.post(url='https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp', json=data, headers=request_header)
        if token.status_code == 200:
            token = token.json()['token']
        else:
            print('Unable to Validate OTP')
            print(token.text)
            os.system("pause")

        return token
    except Exception as e:
        exception_msg = str(e)
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        
        logger.error(f'[ERROR] [authenticate_using_otp] Exception type: {exception_type}, Exception: {exception_msg}, Line number: {line_number}')
        return

        
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
        logger.info(pincode_list)
        c_min_age_limit = int(common_dict['min_age_limit'].strip())
        c_fee = common_dict['fee'].strip()
        c_vaccine = common_dict['vaccine'].strip().lower()
        run_every_seconds = int(common_dict['run_every_seconds'].strip())
        mobile = common_dict['mobile'].strip()
        
        # authentication flow
        parser = argparse.ArgumentParser()
        parser.add_argument('--token', help='Pass token...')
        args = parser.parse_args()

        base_request_header = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        }

        if args.token:
            token = args.token
        else:            
            token = authenticate_using_otp(mobile, base_request_header)

        request_header = copy.deepcopy(base_request_header)
        request_header["Authorization"] = f"Bearer {token}"
        print(f"Bearer {token}")
        print(f'---------------')
        print(f'Beneficiary List...')
        b = get_beneficiaries(request_header)
        print(f'---------------')
        
        while True:
            logger.info('Finding available sessions...')
            #starting from today
            sd = datetime.now()
            ed = datetime.now() + timedelta(days=days)
                            
            sd_s = sd.strftime('%d-%m-%Y')
            ed_s = ed.strftime('%d-%m-%Y')
            #logger.info(sd_s)
            #logger.info(ed_s)
            
            
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
                    
                    #res = requests.get(url, params={}, headers=header, verify=False)
                    res = requests.get(url, params={}, headers=request_header, verify=False)

                    if res.status_code == 200:
                        #logger.info(res)
                        #logger.info(res.text)
                                     
                        res_list = json.loads(res.text)
                        logger.info(res_list)
                        if (len(res_list['sessions']) == 0):
                            logger.info(f'No available sessions.')
                        else:
                            for s in res_list['sessions']:
                                # logger.info(f'{s}')
                                min_age_limit = s['min_age_limit']
                                fee = s['fee']
                                name = s['name']
                                available_capacity = int(s['available_capacity'])
                                vaccine = s['vaccine']
                                
                                c_vaccine = common_dict['vaccine'].strip().lower()
                                
                                if (min_age_limit == c_min_age_limit and fee == c_fee and available_capacity > 0):
                                    # only print matching vaccines
                                    if (vaccine.lower() == c_vaccine or c_vaccine == '*'):
                                        logger.info(f'name = {name}, available_capacity = {available_capacity}, vaccine = {vaccine}, fee = {fee}, min_age_limit = {min_age_limit}')
                                else:
                                    logger.info(f'No available capacity.')
                                
                        logger.info('----------------------------')

                    else:
                        logger.info('403 ERROR: The request could not be satisfied')
                        sys.exit(1)
            

                sd = sd + timedelta(days=1)
                diff = int((ed - sd).days)
            
            # crontab : repeat after n seconds
            print(f'{datetime.now()}')
            time.sleep(run_every_seconds)

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


