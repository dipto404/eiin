import requests
import json

# ক্রেডিটস এবং কনফিগ
CREDITS = {
    'API_OWNER': 'DIPTO',
    'CHANNEL': 'https://t.me/Xrror_404'
}

def get_institute_details(eiin):
    """ধাপ ১: EIIN দিয়ে instituteId এবং eSurveyId সংগ্রহ"""
    url = f"http://202.72.235.218:8082/api/v1/institute/list?page=1&size=1&eiinNo={eiin}"
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        data = response.json()
        if data.get('data') and len(data['data']) > 0:
            return {
                'id': data['data'][0]['id'],
                'esurveyId': data['data'][0]['esurveyId'],
                'name': data['data'][0]['instituteName']
            }
    except Exception:
        return None
    return None

def get_access_token():
    """ধাপ ২: লগইন করে টোকেন সংগ্রহ"""
    url = "http://202.72.235.218:8028/api/v1/auth/login"
    payload = {'username': '124168', 'password': '532688'}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        data = response.json()
        
        # সরাসরি accessToken অথবা ডিবাগ মোড থেকে সংগ্রহ
        if 'accessToken' in data:
            return data['accessToken']
        elif 'debug' in data and 'accessToken' in data['debug']:
            return data['debug']['accessToken']
    except Exception:
        return None
    return None

def main():
    # --- ইনপুট বক্স ---
    eiin_no = input("অনুগ্রহ করে eiinNo দিন: ").strip()
    page = 1
    size = 50

    if not eiin_no:
        print(json.dumps({**{'success': False, 'message': 'দয়া করে eiinNo দিন!'}, **CREDITS}, indent=4, ensure_ascii=False))
        return

    # ১. আইডি খোঁজা
    inst = get_institute_details(eiin_no)
    if not inst:
        print(json.dumps({'success': False, 'message': 'এই EIIN দিয়ে কোনো প্রতিষ্ঠান পাওয়া যায়নি।'}, indent=4, ensure_ascii=False))
        return

    # ২. টোকেন সংগ্রহ
    token = get_access_token()
    if not token:
        print(json.dumps({'success': False, 'message': 'টোকেন পাওয়া যায়নি। লগইন সার্ভার চেক করুন।'}, indent=4, ensure_ascii=False))
        return

    # ৩. এমপ্লয়ি লিস্ট সংগ্রহ
    api_url = "http://202.72.235.218:8028/api/v1/employee/list"
    params = {
        'page': page,
        'size': size,
        'eSurveyId': inst['esurveyId'],
        'instituteId': inst['id']
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(api_url, params=params, headers=headers, timeout=15)
        employees = response.json()
        
        # ৪. রেজাল্ট আউটপুট (PHP ফরম্যাট অনুযায়ী)
        output = {
            'success': (response.status_code == 200),
            'meta_info': {
                'instituteName': inst['name'],
                'eiin': eiin_no,
                'instituteId': inst['id'],
                'eSurveyId': inst['esurveyId']
            },
            'employee_list': employees,
            'credits': CREDITS
        }
        print(json.dumps(output, indent=4, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({'success': False, 'message': str(e)}, indent=4))

if __name__ == "__main__":
    main()
