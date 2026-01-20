import pandas as pd
import glob
import os
import numpy as np

def load_and_concat(pattern):
    """
    Loads all CSV files matching the pattern and concatenates them into a single DataFrame.
    """
    files = glob.glob(pattern)
    if not files:
        print(f"No files found for pattern: {pattern}")
        return pd.DataFrame()
        
    df_list = [pd.read_csv(f) for f in files]
    return pd.concat(df_list, ignore_index=True)

def load_data(base_path):
    """
    Loads biometric, demographic, and enrollment data from the given base path.
    """
    df_bio = load_and_concat(os.path.join(base_path, 'biometric/*.csv'))
    df_demo = load_and_concat(os.path.join(base_path, 'demographic/*.csv'))
    df_enrol = load_and_concat(os.path.join(base_path, 'enrollment/*.csv'))
    
    return df_bio, df_demo, df_enrol

def aggregate_time_series(df_bio, df_demo):
    """
    Aggregates data by date to create a master timeline dataframe.
    """
    # Convert dates
    if not df_bio.empty:
        df_bio['date'] = pd.to_datetime(df_bio['date'], dayfirst=True, errors='coerce')
    if not df_demo.empty:
        df_demo['date'] = pd.to_datetime(df_demo['date'], dayfirst=True, errors='coerce')
    
    # Aggregate biometric updates by date
    bio_agg = pd.DataFrame()
    if not df_bio.empty:
        bio_agg = df_bio.groupby('date')[['bio_age_0_4', 'bio_age_5_17', 'bio_age_18_above']].sum().reset_index()
        bio_agg['total_bio'] = bio_agg['bio_age_0_4'] + bio_agg['bio_age_5_17'] + bio_agg['bio_age_18_above']

    # Aggregate demographic updates by date
    demo_agg = pd.DataFrame()
    if not df_demo.empty:
        demo_agg = df_demo.groupby('date')[['demo_age_0_4', 'demo_age_5_17', 'demo_age_18_above']].sum().reset_index()
        demo_agg['total_demo'] = demo_agg['demo_age_0_4'] + demo_agg['demo_age_5_17'] + demo_agg['demo_age_18_above']
        
    # Merge
    if not bio_agg.empty and not demo_agg.empty:
        df_master = pd.merge(bio_agg, demo_agg, on='date', how='outer').fillna(0)
    elif not bio_agg.empty:
        df_master = bio_agg
        df_master['total_demo'] = 0
    elif not demo_agg.empty:
        df_master = demo_agg
        df_master['total_bio'] = 0
    else:
        return pd.DataFrame()

    df_master['total_updates'] = df_master.get('total_bio', 0) + df_master.get('total_demo', 0)
    df_master = df_master.sort_values('date').set_index('date')
    
    # Resample to weekly
    df_weekly = df_master.resample('W').sum()
    
    return df_weekly

def aggregate_by_pincode(df_bio, df_demo, df_enrol):
    """
    Aggregates data by pincode for risk profiling.
    """
    pincode_stats = pd.DataFrame()
    pincode_demo = pd.DataFrame()
    pincode_pop = pd.DataFrame()

    if not df_bio.empty:
        cols = [c for c in ['bio_age_5_17', 'bio_age_18_above'] if c in df_bio.columns]
        if cols:
             pincode_stats = df_bio.groupby('pincode')[cols].sum().reset_index()
    
    if not df_demo.empty:
        cols = [c for c in ['demo_age_5_17', 'demo_age_18_above'] if c in df_demo.columns]
        if cols:
            pincode_demo = df_demo.groupby('pincode')[cols].sum().reset_index()
    
    if not df_enrol.empty:
        cols = [c for c in ['age_5_17', 'age_18_above'] if c in df_enrol.columns]
        if cols:
            pincode_pop = df_enrol.groupby('pincode')[cols].sum().reset_index()
    
    # Merge all
    # Collect all unique pincodes
    pincodes = set()
    if not pincode_stats.empty: pincodes.update(pincode_stats['pincode'])
    if not pincode_demo.empty: pincodes.update(pincode_demo['pincode'])
    if not pincode_pop.empty: pincodes.update(pincode_pop['pincode'])
    
    df_risk = pd.DataFrame({'pincode': list(pincodes)})
    
    if not pincode_stats.empty:
        df_risk = pd.merge(df_risk, pincode_stats, on='pincode', how='left').fillna(0)
    
    if not pincode_demo.empty:
        df_risk = pd.merge(df_risk, pincode_demo, on='pincode', how='left').fillna(0)
        
    if not pincode_pop.empty:
        df_risk = pd.merge(df_risk, pincode_pop, on='pincode', how='left').fillna(0)
        
    return df_risk

def add_geography_from_pincode(df):
    """
    Adds state and district columns based on pincode prefixes.
    Uses first 2-3 digits of pincode to map to regions based on India Post pincode system.
    """
    if 'pincode' not in df.columns:
        return df
    
    # Convert pincode to string and extract first digits
    df['pincode_str'] = df['pincode'].astype(str).str.zfill(6)
    df['pin_first2'] = df['pincode_str'].str[:2].astype(int)
    df['pin_first3'] = df['pincode_str'].str[:3]
    
    # Function to map pincode to state and district
    def get_geography(row):
        pin2 = row['pin_first2']
        pin3 = row['pin_first3']
        
        # Delhi (11xxxx)
        if pin2 == 11:
            return 'Delhi', 'Central Delhi'
        
        # Haryana (12xxxx-13xxxx)
        elif pin2 in [12, 13]:
            district_map = {'121': 'Faridabad', '122': 'Gurgaon', '123': 'Rohtak', '124': 'Rohtak',
                          '125': 'Hisar', '126': 'Jhajjar', '127': 'Sonipat', '131': 'Sonipat',
                          '132': 'Karnal', '133': 'Ambala', '134': 'Panchkula', '135': 'Yamunanagar',
                          '136': 'Kurukshetra'}
            return 'Haryana', district_map.get(pin3, 'Haryana')
        
        # Punjab (14xxxx-16xxxx)
        elif pin2 in [14, 15, 16]:
            return 'Punjab', 'Punjab'
        
        # Himachal Pradesh (17xxxx)
        elif pin2 == 17:
            return 'Himachal Pradesh', 'Shimla'
        
        # Jammu & Kashmir (18xxxx-19xxxx)
        elif pin2 in [18, 19]:
            return 'Jammu & Kashmir', 'Srinagar'
        
        # Uttar Pradesh (20xxxx-28xxxx)
        elif 20 <= pin2 <= 28:
            return 'Uttar Pradesh', 'Lucknow'
        
        # Uttarakhand (24xxxx-26xxxx)
        elif pin2 in [24, 25, 26]:
            district_map = {'262': 'Nainital', '263': 'Almora', '244': 'Nainital',
                          '245': 'Haridwar', '246': 'Pauri', '247': 'Dehradun',
                          '248': 'Dehradun', '249': 'Tehri'}
            return 'Uttarakhand', district_map.get(pin3, 'Dehradun')
        
        # Rajasthan (30xxxx-34xxxx)
        elif 30 <= pin2 <= 34:
            return 'Rajasthan', 'Jaipur'
        
        # Gujarat (36xxxx-39xxxx)
        elif 36 <= pin2 <= 39:
            district_map = {'380': 'Ahmedabad', '390': 'Vadodara', '394': 'Surat',
                          '395': 'Surat', '396': 'Valsad', '360': 'Rajkot',
                          '361': 'Jamnagar', '362': 'Porbandar', '363': 'Surendranagar',
                          '364': 'Bhavnagar', '365': 'Amreli', '370': 'Kutch'}
            return 'Gujarat', district_map.get(pin3, 'Gujarat')
        
        # Maharashtra (40xxxx-44xxxx)
        elif 40 <= pin2 <= 44:
            district_map = {'400': 'Mumbai', '401': 'Thane', '402': 'Raigad',
                          '403': 'Goa', '410': 'Pune', '411': 'Pune',
                          '412': 'Pune', '413': 'Solapur', '414': 'Ahmednagar',
                          '415': 'Satara', '416': 'Sangli', '421': 'Thane',
                          '422': 'Nashik', '423': 'Aurangabad', '424': 'Jalgaon',
                          '425': 'Dhule', '431': 'Aurangabad', '440': 'Nagpur',
                          '441': 'Nagpur', '442': 'Wardha', '443': 'Akola',
                          '444': 'Washim', '445': 'Yeotmal'}
            return 'Maharashtra', district_map.get(pin3, 'Maharashtra')
        
        # Madhya Pradesh (45xxxx-48xxxx)
        elif 45 <= pin2 <= 48:
            return 'Madhya Pradesh', 'Bhopal'
        
        # Chhattisgarh (49xxxx)
        elif pin2 == 49:
            return 'Chhattisgarh', 'Raipur'
        
        # Andhra Pradesh & Telangana (50xxxx-53xxxx)
        elif 50 <= pin2 <= 53:
            district_map = {'500': 'Hyderabad', '501': 'Rangareddy', '502': 'Medak',
                          '503': 'Nizamabad', '504': 'Adilabad', '505': 'Karimnagar',
                          '506': 'Warangal', '507': 'Khammam', '508': 'Nalgonda',
                          '509': 'Mahabubnagar', '515': 'Anantapur', '516': 'Kadapa',
                          '517': 'Chittoor', '518': 'Kurnool', '520': 'Krishna',
                          '521': 'Krishna', '522': 'Guntur', '523': 'Prakasam',
                          '524': 'Nellore', '530': 'Visakhapatnam', '531': 'Visakhapatnam',
                          '532': 'Srikakulam', '533': 'East Godavari', '534': 'West Godavari',
                          '535': 'Vizianagaram'}
            state = 'Telangana' if pin2 == 50 else 'Andhra Pradesh'
            return state, district_map.get(pin3, state)
        
        # Karnataka (56xxxx-59xxxx)
        elif 56 <= pin2 <= 59:
            district_map = {'560': 'Bangalore', '561': 'Bangalore Rural', '562': 'Chikballapur',
                          '563': 'Kolar', '570': 'Mysore', '571': 'Mysore',
                          '572': 'Tumkur', '573': 'Hassan', '574': 'Dakshina Kannada',
                          '575': 'Udupi', '576': 'Dakshina Kannada', '577': 'Chitradurga',
                          '580': 'Dharwad', '581': 'Haveri', '582': 'Gadag',
                          '583': 'Bellary', '584': 'Raichur', '585': 'Bijapur',
                          '586': 'Belgaum', '587': 'Gulbarga', '590': 'Belgaum',
                          '591': 'Belgaum'}
            return 'Karnataka', district_map.get(pin3, 'Karnataka')
        
        # Tamil Nadu (60xxxx-64xxxx)
        elif 60 <= pin2 <= 64:
            district_map = {'600': 'Chennai', '601': 'Kanchipuram', '602': 'Chennai',
                          '603': 'Kanchipuram', '604': 'Villupuram', '605': 'Pondicherry',
                          '606': 'Cuddalore', '607': 'Tiruvannamalai', '608': 'Ariyalur',
                          '609': 'Nagapattinam', '610': 'Thanjavur', '611': 'Thanjavur',
                          '612': 'Pudukkottai', '613': 'Thanjavur', '614': 'Tiruvarur',
                          '620': 'Tiruchirappalli', '621': 'Tiruchirappalli', '622': 'Pudukkottai',
                          '623': 'Sivaganga', '624': 'Ramanathapuram', '625': 'Madurai',
                          '626': 'Madurai', '627': 'Tirunelveli', '628': 'Tuticorin',
                          '629': 'Kanyakumari', '630': 'Karur', '631': 'Namakkal',
                          '632': 'Salem', '635': 'Dharmapuri', '636': 'Salem',
                          '637': 'Namakkal', '638': 'Erode', '639': 'Coimbatore',
                          '641': 'Coimbatore', '642': 'Coimbatore', '643': 'Nilgiris'}
            return 'Tamil Nadu', district_map.get(pin3, 'Tamil Nadu')
        
        # Kerala (67xxxx-69xxxx)
        elif 67 <= pin2 <= 69:
            district_map = {'670': 'Kannur', '671': 'Kozhikode', '673': 'Kozhikode',
                          '676': 'Malappuram', '678': 'Palakkad', '679': 'Palakkad',
                          '680': 'Thrissur', '682': 'Ernakulam', '683': 'Ernakulam',
                          '685': 'Idukki', '686': 'Kottayam', '688': 'Alappuzha',
                          '689': 'Pathanamthitta', '690': 'Kollam', '691': 'Kollam',
                          '695': 'Thiruvananthapuram'}
            return 'Kerala', district_map.get(pin3, 'Kerala')
        
        # West Bengal (70xxxx-74xxxx)
        elif 70 <= pin2 <= 74:
            return 'West Bengal', 'Kolkata'
        
        # Odisha (75xxxx-77xxxx)
        elif 75 <= pin2 <= 77:
            district_map = {'751': 'Khordha', '752': 'Puri', '753': 'Cuttack',
                          '754': 'Jagatsinghpur', '755': 'Kendrapara', '756': 'Baleswar',
                          '757': 'Mayurbhanj', '758': 'Keonjhar', '759': 'Dhenkanal',
                          '760': 'Angul', '761': 'Boudh', '762': 'Kandhamal',
                          '763': 'Ganjam', '764': 'Gajapati', '765': 'Rayagada',
                          '766': 'Koraput', '767': 'Nabarangpur', '768': 'Kalahandi',
                          '769': 'Nuapada', '770': 'Sambalpur'}
            return 'Odisha', district_map.get(pin3, 'Odisha')
        
        # Assam & Northeast (78xxxx-79xxxx)
        elif 78 <= pin2 <= 79:
            district_map = {'781': 'Kamrup', '782': 'Nagaon', '783': 'Goalpara',
                          '784': 'Barpeta', '785': 'Kokrajhar', '786': 'Dhubri',
                          '787': 'North Lakhimpur', '788': 'Jorhat', '790': 'Shillong',
                          '791': 'Tura', '792': 'Jowai', '793': 'Aizawl',
                          '794': 'Arunachal Pradesh', '795': 'Manipur', '796': 'Manipur',
                          '797': 'Nagaland', '798': 'Tripura', '799': 'Tripura'}
            if pin3 in ['790', '791', '792']:
                return 'Meghalaya', district_map.get(pin3, 'Meghalaya')
            elif pin3 == '793':
                return 'Mizoram', 'Aizawl'
            elif pin3 == '794':
                return 'Arunachal Pradesh', 'Itanagar'
            elif pin3 in ['795', '796']:
                return 'Manipur', 'Imphal'
            elif pin3 == '797':
                return 'Nagaland', 'Kohima'
            elif pin3 in ['798', '799']:
                return 'Tripura', 'Agartala'
            else:
                return 'Assam', district_map.get(pin3, 'Assam')
        
        # Bihar (80xxxx-85xxxx)
        elif 80 <= pin2 <= 85:
            return 'Bihar', 'Patna'
        
        # Default
        else:
            return 'India', 'India'
    
    # Apply mapping
    df[['state', 'district']] = df.apply(get_geography, axis=1, result_type='expand')
    
    # Clean up temporary columns
    df = df.drop(columns=['pincode_str', 'pin_first2', 'pin_first3'])
    
    return df
