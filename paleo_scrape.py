import requests
import pandas as pd


import pandas
import requests

def get_bool(prompt):
    while True:
        try:
            return {"true":True, "t": True, "false":False, "f":False, "yes":True, "no":False, "y":True, "n":False}[raw_input(prompt).lower()]
        except KeyError:
            print "Invalid input, please enter True or False"

def get_year(prompt):
    while True:
        try:
            return int(raw_input(prompt))
        except:
            print "Please enter a year"


def get_all_paleodata(CE=False):
    continent = raw_input('enter continent: ').lower()
    ey = get_bool('set earliest year?: (True or False) ')
    print ey
    if ey:
        earliest_year = get_year('enter earliest year needed: ')
    else:
        earliest_year = None
    ly = get_bool('set latest year?: (True or False) ')
    if ly:
        latest_year = get_year('enter latest year needed: ')
    
    else:
        latest_year = None
    
    if earliest_year:
        assert int(earliest_year)
    if latest_year:
        assert int(latest_year)
        if earliest_year:
            assert int(latest_year) < int(earliest_year)

    if CE == False:
        if earliest_year != None:
            eyear = "earliestYear=%s&" % earliest_year
            if latest_year == None:
                url = "https://www.ncdc.noaa.gov/paleo-search/study/search.json?headersOnly=true&dataPublisher=NOAA&{0}timeMethod=overAny&locations=Continent%3E{1}".format(eyear, continent)
            elif latest_year != None:
                lyear = "latestYear=%s&" % latest_year
                url = "https://www.ncdc.noaa.gov/paleo-search/study/search.json?headersOnly=true&dataPublisher=NOAA&{0}{1}timeMethod=overAny&locations=Continent%3E{2}".format(eyear, lyear, continent)
        elif earliest_year == None and latest_year != None:
            lyear = "latestYear=%s&" % latest_year
            url = "https://www.ncdc.noaa.gov/paleo-search/study/search.json?headersOnly=true&dataPublisher=NOAA&{0}timeMethod=overAny&locations=Continent%3E{1}".format(lyear, continent)
        
        else:
            url = "https://www.ncdc.noaa.gov/paleo-search/study/search.json?headersOnly=true&dataPublisher=NOAA&timeMethod=overAny&locations=Continent%3E{0}".format(continent)

    return url

def make_request(token=None):
    url = get_all_paleodata()
    print('getting data, please wait')
    r = requests.get(url)
    response = r.json()
    num_studies = len(response['study'])
    print '\n','total number of studies = %s'% num_studies
    return response


def list_studies():
    response = make_request()
    
    apiList = response['study']
    xmlid_list = []
    for i in apiList:
        xmlid_list.append(i['xmlId'])
    xmlid_list = [x.encode('UTF8') for x in xmlid_list]
    return xmlid_list



# for different types of data:
# dataType = {0:'zero', 1:'one', 2:'two'} &dataTypeId=1|2|4|12|6|7|8|20|9|10|19|14|11|13|15|16|60|59|17|18&


def make_df():
    xmlid_list = list_studies()
    # if connection times out:
    print '\n'
    start_bool = get_bool('set start of index? (True or False)')
    if start_bool:
        start = int(raw_input('starting index (number): '))
        assert xmlid_list[start], "out of index"
    else:
        start = 0

    end_bool = get_bool('set end of index? (True or False)')
    if end_bool:
        end = int(raw_input('ending index (number): '))
        assert xmlid_list[end], "out of index"
        if start_bool:
            assert end > start, "end index before start index"

    else:
        end = len(xmlid_list)-1
    full_list = []
    print_count = 0
    length = len(range(start,end))
    
    for i in xmlid_list[start:end]:
        url = "https://www.ncdc.noaa.gov/paleo-search/study/search.json?xmlId={0}".format(i)
        
        r = requests.get(url)
        response = r.json()
        apiList = response['study']
        
        d = {}
        d['earliest_BP'] = apiList[0]['earliestYearBP']
        d['dataType'] = apiList[0]['dataType']
        d['most_recent_BP'] = apiList[0]['mostRecentYearBP']
        d['date'] = apiList[0]['contributionDate']
        if apiList[0]['site'][0]['geo']['properties']['maxElevationMeters'] == apiList[0]['site'][0]['geo']['properties']['minElevationMeters']:
            d['maxElevation'] = apiList[0]['site'][0]['geo']['properties']['maxElevationMeters']
        else:
            d['maxElevation'] = apiList[0]['site'][0]['geo']['properties']['maxElevationMeters']
            d['minElevation'] = apiList[0]['site'][0]['geo']['properties']['minElevationMeters']
        list_coord = apiList[0]['site'][0]['geo']['geometry']['coordinates']
        list_coord = [x.encode('UTF8') for x in list_coord]
        d['xmlId'] = apiList[0]['xmlId']
        d['study name'] = apiList[0]['studyName']
        d['online_link'] = apiList[0]['onlineResourceLink']
        
        
        counter = 0
        x = []
        y = []
        for i in list_coord:
            if counter % 2 == 0:
                x_val = i
            else:
                y_val = i
            
            counter += 1
            if counter > 2:
                x.append(x_val)
                y.append(y_val)
        if counter == 2:
            d['lat'] = y_val
            d['lon'] = x_val
        else:
            d['lat'] = y
            d['lon'] = x
        full_list.append(d)
        print_count += 1
        print 'status: %s%s %s out of %s' % ((float(print_count) / float(length)*100), '%', print_count, length)
        
        df = pandas.DataFrame(full_list)
    try:
        return df
    except:
        print '\n','no data returned'

def save_loc(prompt, df):
    while True:
        save = get_bool('1. would you like to save data to csv? ')
        if save:
            save_location = raw_input(prompt)
            try:
                df.to_csv('%s.csv' % save_location, index=True)
                return 'Successfully Saved!'
            except:
                print 'please enter valid save location'
        else:
            return

def main():
    df = make_df()
    save_loc('2. where to save: ', df)
    print(df.head())
    print '\n ', 'done!'
    return df

if __name__ == "__main__":
    main()

