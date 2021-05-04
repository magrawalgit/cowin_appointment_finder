# CoWin Appointment Finder

This is a small python utility to find available appointments of the desired pin code(s) for next N days, for a given age limit.
git clone git@github.com:mata1234/cowin_appointment_finder.git

**1 - Install python**
**2 - pip install below packages (if not already)**

datetime
time
logging
logging.handlers
urllib3
configparser

**3 - setup config in the setup.cfg**
pincode_list=List of pin codes seperated by comma
days_ahead=check appointments for next N days
min_age_limit=45 and above specify 45
fee=0 for free vaccines
e.g.
pincode_list=413102,413115,413102
days_ahead=5
min_age_limit=45
fee=0

**4 - open command prompt and run the utility**
python cowin_appointment_finder.py

Output will be stored in a text log as below:
```
[2021-05-04 21:21:30,446] ----------------------------
[2021-05-04 21:21:30,446] date = 09-05-2021, pin_code = 413102
[2021-05-04 21:21:30,461] https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=413102&date=09-05-2021
[2021-05-04 21:21:30,824] name = PARWADI, available_capacity = 44, vaccine = COVISHIELD, fee = 0, min_age_limit = 45
[2021-05-04 21:21:30,824] name = Undavadisupe, available_capacity = 47, vaccine = COVISHIELD, fee = 0, min_age_limit = 45
[2021-05-04 21:21:30,824] name = Shirsufal PHC, available_capacity = 48, vaccine = COVISHIELD, fee = 0, min_age_limit = 45
[2021-05-04 21:21:30,824] name = Pimpali, available_capacity = 46, vaccine = COVISHIELD, fee = 0, min_age_limit = 45
[2021-05-04 21:21:30,824] name = Sirsane, available_capacity = 50, vaccine = COVISHIELD, fee = 0, min_age_limit = 45
[2021-05-04 21:21:30,824] name = KARHAWAGAJ, available_capacity = 50, vaccine = COVISHIELD, fee = 0, min_age_limit = 45
[2021-05-04 21:21:30,824] ----------------------------
```
