import json
import pandas as pd
import numpy as np
import matplotlib as mpl #colour
import copy
import time
from PIL import ImageColor
import glob
import os
import sys


def helper_dump_master_to_zipped_csv(pop):
    #needs work, but this is the code I used to manually dump the master dataset to a zipped csv
    
    #subset master dataset to selected series, and sort by year, then country
    df = pop.sort_values(by=['Series','Year', 'Country'])  
    # make it pretty
    df['m49_un_a3'] = df['m49_un_a3'].astype(str).str.zfill(3) 
    df['United Nations m49 country code'] = df['m49_un_a3']
    #df = df.rename(columns={'Value':dataset_lookup.loc[dataset_lookup['dataset_raw'] == series].iloc[0,2]})   
    df = df.drop(columns=['m49_un_a3', 'region_un', 'region_wb', 'continent'])   
    #print(len(df))
    path = "./tmp/test.zip"
    df.to_csv(path, index=False, compression={'method': 'zip', 'archive_name':'test.csv', 'compresslevel': 1}) 
    return


def create_api_lookup_dicts(dataset_lookup):
    
    #subset dataset lookup
    df = dataset_lookup[['dataset_raw', 'dataset_label', 'dataset_label']].copy()
    df.columns=['dataset_raw', 'dataset_label', 'api_label']
    
    #drop duplicate rows
    df = df.drop_duplicates()
    
    # make api labels URL path friendly
    df['api_label'] = df.api_label.str.replace(' ','-')
    df['api_label'] = df.api_label.str.replace('%','percent')
    df['api_label'] = df.api_label.str.replace('?','-')
    df['api_label'] = df.api_label.str.replace('+','-')
    df['api_label'] = df.api_label.str.replace(',','-')
    
    # declare new global dicts
    api_dict_raw_to_label={}
    api_dict_label_to_raw={}
    
    # build lookup dictionaries by iterating the DF (ineffecient but will do for now)
    for index,row in df.iterrows():
        api_dict_raw_to_label[row['dataset_raw']]=row['api_label']
        api_dict_label_to_raw[row['api_label']]=row['dataset_raw']
        
    return api_dict_raw_to_label, api_dict_label_to_raw




def convert_csv_to_parquet(path):    
    df = pd.read_csv(path,encoding="latin-1")      
    pq_path = (path[:-3])+"parquet"
    df.to_parquet(pq_path)
    return
    
def convert_xlsx_to_parquet(path):    
    df = pd.read_excel(path)      
    pq_path = (path[:-4])+"parquet"
    df.to_parquet(pq_path)
    return


def convert_folder_csv_to_parquet(relative_path):
    #Helper function to convert a whole folder of .csv files to .parquet with same names
    
    path = os.getcwd()+relative_path 
    
    for filepath in glob.iglob(path+'*.csv'):
        print(filepath)
        convert_csv_to_parquet(filepath)    
    
    return


def import_gapminder_fastrack_parquet(relative_path_data, relative_path_concepts, cunts): 
    
    #cunts=country_lookup
    #relative_path_data="/data/datasets/gapminder-fast-track/parquet/"
    #relative_path_concepts="/data/datasets/gapminder-fast-track/"
    
    path = os.getcwd()+relative_path_data 
    path_concepts = os.getcwd()+relative_path_concepts 
    print(path)       
    print(path_concepts)
    
    # open lookup df
    lookup = pd.read_parquet(path_concepts+"ddf--concepts.parquet")    
    
    #declare empty dataframes    
    pop = pd.DataFrame() 
        
    for filepath in glob.iglob(path+'*.parquet'):
        print("Importing",filepath)
        
        # read in df
        df = pd.read_parquet(filepath)
        
        # extract id
        concept = df.columns[2]
        print('concept is',concept)
        
        # attempt to find details in lookup
        try:
            query = lookup[lookup['concept']==concept]            
        
        except KeyError as error:
            print("Exception thrown attempting to lookup ",concept)   
        
        # break if series not found in lookup
        if len(query) != 1:
            print("Query invalid, jumping to next file")
            continue                
        
        # at this point we are good and ready to start building the pop structure               
        df['Series'] = query['name'].iloc[0]
        df['Source'] = "Gapminder Fastrack Indicators." + " Updated " + query['updated'].iloc[0]
        df['Link'] = query['source_url'].iloc[0]
        df['explanatory_note'] =query['description'].iloc[0]               
        
        #convert country codes to uppercase (to match datasetlookup)
        df['country'] = df['country'].str.upper() #this is su_a3 e.g. AUD
        df['m49_un_a3'] = "testing"
        df['Country'] = "testing"   
        
        # add m49 integers 
        for i in cunts['su_a3']:               
            
            #set the regions for each unique country to columns in the master df
            try:
                df.loc[df['country']==i, 'm49_un_a3'] = cunts.loc[cunts['su_a3'] == i].iloc[0,0]
                df.loc[df['country']==i, 'Country'] = cunts.loc[cunts['su_a3'] == i].iloc[0,1]              
            
            except IndexError as error:
                print("Exception: Attempting to add cunt data")              
        
        # reorganise cols and subset
        df = df.rename(columns={"time":"Year", concept:'Value'})
        df = df[['m49_un_a3', 'Country', 'Year', 'Series', 'Value', 'Source', 'Link', 'explanatory_note' ]]
        df['Year'] = df['Year'].astype(str)
        df['Value'] = df['Value'].astype(str)        
        
        #strip out any non-country regions from the dataset, based on cunts shortlist
        print("Length of df before strip", len(df))
        df = df[df['m49_un_a3'].isin(cunts['m49_a3_country'])]    
        print("Length of df after strip", len(df))
                
        # append to clean pop dataframe
        pop = pop.append(df)

    # append to .csv helper for dataset_lookup        
    pop.drop_duplicates(['Series']).to_csv('gapminder_source_fasttrack_helper.csv')    
    
    # strip out unneeded cols and return
    pop = pop.drop(columns=['Source', 'Link', 'explanatory_note'])    
    
    return pop


def import_gapminder_world_dev_indicators_parquet(relative_path_data, relative_path_concepts, cunts): 
    
    #cunts=country_lookup
    cunts = create_unique_country_list("data/country_lookup.csv")  # this is a duplicate and needs to be fixed as global var
    relative_path_data="/data/datasets/world-development-indicators/parquet/"
    relative_path_concepts="/data/datasets/world-development-indicators/"
    
    path = os.getcwd()+relative_path_data 
    path_concepts = os.getcwd()+relative_path_concepts     
    print(path)       
    print(path_concepts)   
 
    
    # open lookup df
    lookup = pd.read_parquet(path_concepts+"ddf--concepts--continuous.parquet")    
    
    #declare empty dataframes    
    pop = pd.DataFrame() 
        
    for filepath in glob.iglob(path+'*.parquet'):
        print("Importing",filepath)
        
        # read in df
        df = pd.read_parquet(filepath)
        
        # extract id
        concept = df.columns[2]
        print('concept is',concept)
        
        # attempt to find details in lookup
        try:
            query = lookup[lookup['concept']==concept]            
        
        except KeyError as error:
            print("Exception thrown attempting to lookup ",concept)   
        
        # break if series not found in lookup
        if len(query) != 1:
            print("Query invalid, jumping to next file")
            continue                
        
        # at this point we are good and ready to start building the pop structure               
        df['Series'] = query['name'].iloc[0]        
        query['development_relevance'] = query['development_relevance'].fillna('')
        query['long_definition'] = query['long_definition'].fillna('')
        query['statistical_concept_and_methodology'] = query['statistical_concept_and_methodology'].fillna('')
        query['series_code'] = query['series_code'].fillna('')        
        query['general_comments'] = query['general_comments'].fillna('')
        query['limitations_and_exceptions'] = query['limitations_and_exceptions'].fillna('')         
        
        
        df['Source'] = "World Bank - World Development Indicators." + " Series code: " + query['series_code'].iloc[0]
        df['Link'] = "https://github.com/open-numbers/ddf--open_numbers--world_development_indicators"             
        
        df['explanatory_note'] = query['development_relevance'].iloc[0] + " " + query['long_definition'].iloc[0] + " " + query['statistical_concept_and_methodology'].iloc[0] + " " + query['general_comments'].iloc[0] + " " + query['limitations_and_exceptions'].iloc[0]
        
        # strip out new lines \n
        df['explanatory_note'] = df['explanatory_note'].str.replace(r'\\n', '')        
               
        #convert country codes to uppercase (to match datasetlookup)
        try:
            df['geo'] = df['geo'].str.upper() #this is su_a3 e.g. AUD
        
        except KeyError as error:
            print("Exception thrown attempting to lookup Geo. Likely a global dataset only. Skipping")
            continue    
        
        df['m49_un_a3'] = "testing"
        df['Country'] = "testing"   
        
        # add m49 integers 
        for i in cunts['su_a3']:               
            
            #set the regions for each unique country to columns in the master df
            try:
                df.loc[df['geo']==i, 'm49_un_a3'] = cunts.loc[cunts['su_a3'] == i].iloc[0,0]
                df.loc[df['geo']==i, 'Country'] = cunts.loc[cunts['su_a3'] == i].iloc[0,1]              
            
            except IndexError as error:
                print("Exception: Attempting to add cunt data")              
        
        # reorganise cols and subset
        df = df.rename(columns={"time":"Year", concept:'Value'})
        df = df[['m49_un_a3', 'Country', 'Year', 'Series', 'Value', 'Source', 'Link' , 'explanatory_note']]
        df['Year'] = df['Year'].astype(str)
        df['Value'] = df['Value'].astype(str)        
        
        #strip out any non-country regions from the dataset, based on cunts shortlist
        print("Length of df before strip", len(df))
        df = df[df['m49_un_a3'].isin(cunts['m49_a3_country'])]    
        print("Length of df after strip", len(df))
                
        # append to clean pop dataframe
        pop = pop.append(df)

    # append to .csv helper for dataset_lookup        
    pop.drop_duplicates(['Series']).to_csv('gapminder_worlddev_source_helper.csv')    
    
    # strip out unneeded cols and return
    pop = pop.drop(columns=['Source', 'Link', 'explanatory_note'])    
    
    # clean out any commas from string numbers (known issue)
    pop["Value"] = pop["Value"].str.replace(",","")
    
    return pop




def import_gapminder_systema_globalis_parquet(relative_path_data, relative_path_concepts, cunts): 
    
    #relative_path_data="/data/datasets/gapminder-systema-globalis/parquet/"
    #relative_path_concepts="/data/datasets/gapminder-systema-globalis/"
    #cunts=country_lookup
    
    path = os.getcwd()+relative_path_data 
    path_concepts = os.getcwd()+relative_path_concepts     
    print(path)       
    print(path_concepts)
    
    # open lookup df
    lookup = pd.read_parquet(path_concepts+"ddf--concepts.parquet")    
    
    #declare empty dataframes    
    pop = pd.DataFrame() 
        
    for filepath in glob.iglob(path+'*.parquet'):
        print("Importing",filepath)
        
        # read in df
        df = pd.read_parquet(filepath)
        
        # extract id
        concept = df.columns[2]
        print('concept is',concept)
        
        # attempt to find details in lookup
        try:
            query = lookup[lookup['concept']==concept]            
        
        except KeyError as error:
            print("Exception thrown attempting to lookup ",concept)   
        
        # break if series not found in lookup
        if len(query) != 1:
            print("Query invalid, jumping to next file")
            continue                
        
        # at this point we are good and ready to start building the pop structure               
        df['Series'] = query['name'].iloc[0]
        query['description'] = query['description'].fillna('')
        df['Source'] = "Gapminder Systema Globalis Indicators."
        df['Link'] = query['source_url'].iloc[0]
        
        # add explanatory notes
        if query['description_long'].iloc[0] != None: df['explanatory_note'] = query['description'].iloc[0] + " " + query['description_long'].iloc[0]
        else: df['explanatory_note'] = query['description'].iloc[0] 
        
        #convert country codes to uppercase (to match datasetlookup)
        df['geo'] = df['geo'].str.upper() #this is su_a3 e.g. AUD
        df['m49_un_a3'] = "testing"
        df['Country'] = "testing"   
        
        # add m49 integers 
        for i in cunts['su_a3']:               
            
            #set the regions for each unique country to columns in the master df
            try:
                df.loc[df['geo']==i, 'm49_un_a3'] = cunts.loc[cunts['su_a3'] == i].iloc[0,0]
                df.loc[df['geo']==i, 'Country'] = cunts.loc[cunts['su_a3'] == i].iloc[0,1]              
            
            except IndexError as error:
                print("Exception: Attempting to add cunt data")              
        
        # reorganise cols and subset
        df = df.rename(columns={"time":"Year", concept:'Value'})
        df = df[['m49_un_a3', 'Country', 'Year', 'Series', 'Value', 'Source', 'Link' ,'explanatory_note']]
        df['Year'] = df['Year'].astype(str)
        df['Value'] = df['Value'].astype(str)        
        
        #strip out any non-country regions from the dataset, based on cunts shortlist
        print("Length of df before strip", len(df))
        df = df[df['m49_un_a3'].isin(cunts['m49_a3_country'])]    
        print("Length of df after strip", len(df))
                
        # append to clean pop dataframe
        pop = pop.append(df)

    # append to .csv helper for dataset_lookup        
    #pop.drop_duplicates(['Series']).to_csv('gapminder_systglob_source_helper.csv')    
    
    # strip out unneeded cols and return
    pop = pop.drop(columns=['Source', 'Link', 'explanatory_note'])    
    
    return pop



def import_master_dataset(country_lookup, FAST_LOAD, LOAD_RAW):
    
    if LOAD_RAW == True:
    
        # add UN data
        tic = time.perf_counter()
        pop = import_UNdata_parquet("data/datasets/undata/parquet/SYB60_312_Carbon_Dioxide_Emission_Estimates.parquet", country_lookup)
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB61_12_Agricultural_Production_Indices.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_1_201907_Population_Surface_Area_and_Density.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_125_201907_Balance_of_Payments.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_128_201907_Consumer_Price_Index.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_145_201904_Land.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_153_201906_Gross_Value_Added_by_Economic_Activity.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_200_201905_Employment.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_230_201904_GDP_and_GDP_Per_Capita.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_246_201907_Population_Growth_Fertility_and_Mortality_Indicators.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_263_201904_Production_Trade_and_Supply_of_Energy.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_309_201906_Education.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_313_201907_Threatened_Species.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_314_201904_Internet_Usage.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_327_201907_International_Migrants_and_Refugees.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_328_201904_Intentional_Homicides_and_Other_Crimes.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB62_329_201904_Labour_Force_and_Unemployment.parquet", country_lookup))
        pop = pop.append(import_UNdata_parquet("data/datasets/undata/parquet/SYB63_325_202003_Expenditure_on_Health.parquet", country_lookup))
        toc = time.perf_counter()
        print('UN data total load time (parquet):',toc-tic, 'seconds')
        
        #add discrete dataset
        pop = pop.append(import_discrete_data("data/datasets/driving_side.csv", country_lookup))
        pop = pop.append(import_discrete_data("data/experimental/discrete_test.csv", country_lookup)) #add some discrete test data
        
        # add SDG indicators
        #if FAST_LOAD != True:
        tic = time.perf_counter()
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal1.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal2.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal3.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal4.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal5.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal6.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal7.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal8.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal9.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal10.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal11.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal12.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal13.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal14.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal15.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal16.parquet", country_lookup))
        pop = pop.append(import_SDGdata_parquet("data/datasets/sdgindicators/parquet/Goal17.parquet", country_lookup))
        toc = time.perf_counter()
        print('SDG data total load time (parquet):',toc-tic, 'seconds')
        
        # add gapminder fastrack
        if FAST_LOAD != True:
            tic = time.perf_counter()
            pop = pop.append(import_gapminder_fastrack_parquet("/data/datasets/gapminder-fast-track/parquet/", "/data/datasets/gapminder-fast-track/", country_lookup))
            toc = time.perf_counter()
            print('Gapminder fastrack total load time (parquet):',toc-tic, 'seconds')    
        
        # add gapminder systema globalis
        if FAST_LOAD != True:
            tic = time.perf_counter()
            pop = pop.append(import_gapminder_systema_globalis_parquet("/data/datasets/gapminder-systema-globalis/parquet/", "/data/datasets/gapminder-systema-globalis/", country_lookup))
            toc = time.perf_counter()
            print('Gapminder systema globalis total load time (parquet):',toc-tic, 'seconds')     
        
        # add gapminder world dev indicators
        if FAST_LOAD != True:
            tic = time.perf_counter()
            pop = pop.append(import_gapminder_world_dev_indicators_parquet("/data/datasets/world-development-indicators/parquet/", "/data/datasets/world-development-indicators/", country_lookup))
            toc = time.perf_counter()
            print('Gapminder world dev indicators total load time (parquet):',toc-tic, 'seconds') 
            
        #add region information (Whilst this is not space efficient, it is performance efficient and used by bubble, pizza, and can also add to downloads easily)
        if FAST_LOAD != True:
            tic = time.perf_counter()
            add_regions(pop, country_lookup)
            toc = time.perf_counter()
            print('Regions added. Load time:',toc-tic,'seconds')
        
        # clean up
        pop = pop.reset_index(drop=True)
        
        #Note the below lines havent been tested as manually fixed the master without needing to reload. (Major update to new data types to save mem)
        pop['m49_un_a3'] = pop['m49_un_a3'].astype('category') #not tested
        pop['Country'] = pop['Country'].astype('category') #not tested
        pop['Year'] = pop['Year'].astype('uint16') #not tested
        pop['Series'] = pop['Series'].astype('category') #not tested
        pop['Value'] = pop['Value'].astype(str)
        pop['continent'] = pop['continent'].astype('category') #not tested
        pop['region_un'] = pop['region_un'].astype('category') #not tested
        pop['region_wb'] = pop['region_wb'].astype('category') #not tested        
       
        pop.to_parquet('data/master.parquet', index=False, engine="pyarrow")
        
        # report size of master dataframe
        print("Size of master dataframe :", str(round(sys.getsizeof(pop)/(1024**2), 0)),"MB")
    
    else:
        tic = time.perf_counter()
        path = os.getcwd()+"/data/master.parquet" 
        pop = pd.read_parquet(path)
        toc = time.perf_counter()
        print('Loaded master dataset from parquet in ',toc-tic,'seconds')
        
    
    return pop
    

def import_SDGdata_xlsx(path, cunts):
    # lThis is a helper function now to clean xls and prep for parquet.
    print("Loading data: ", path)    
    tic = time.perf_counter()
    
    #cunts=create_dataset_lookup("data/dataset_lookup.csv")
    path="data/datasets/sdgindicators/excel/Goal1.xlsx"
    
    df = pd.read_excel(
        path,        
        #usecols=["Goal", "Target", "Indicator", "SeriesCode", "GeoAreaCode", "GeoAreaName", "TimePeriod", "SeriesDescription", "Value", "FootNote", "Source", "Age", 'Sex', 'Location']
        )    
        
 
    # concatenate series with extras
    print('NaN row count',df.isna().sum())
    df['Age'] = df['Age'].fillna('')
    df['Sex'] = df['Sex'].fillna('')
    df['Location'] = df['Location'].fillna('')
    df['newSeries'] = df['SeriesDescription'] + ' ' + df['Age'].astype(str) + ' ' + df['Sex'].astype(str) + ' ' + df['Location'].astype(str)
    df['newSeries'] = df['newSeries'].str.strip()    
    df['SeriesDescription'] = df['newSeries']
    df = df.drop(columns=['newSeries'])
    
    #df = df.rename(columns={"GeoAreaCode":'m49_un_a3', "GeoAreaName":'Country', "TimePeriod":'Year', "newSeries":'Series', "newSource":"Source"})
    
    # organise cols
    #df = df[["m49_un_a3", "Country", 'Year', 'Series', 'Value', 'Source']]    
    
    #padd the 3 digit m49 country integer with zeros if it less than 100 (i.e. "3" will become "003")    
    #df['m49_un_a3'] = df['m49_un_a3'].astype(str).str.zfill(3) 
    
    #strip out any non-country regions from the dataset, based on cunts shortlist
    #df = df[df['m49_un_a3'].isin(cunts['m49_a3_country'])]   
    
    #drop any rows with nan value
    #print("pre nan len", len(df))
    #df = df.dropna(subset=['Value'])
    #print("post nan len", len(df))
    
    #cast to strings
    #df['Value'] = df['Value'].astype(str)
    #df['Year'] = df['Year'].astype(str)
    
    #summary 
    #print(pd.unique(df['Series']))
    #print(len(pd.unique(df['Series'])), " unique series.")  
    
    #helper to save unique series, note, source -> dataset_lookup
    #df.drop_duplicates(['Series']).to_csv('sdg.csv')    
    #df = df.drop(columns=['Source'])
    
    #toc = time.perf_counter()    
    #print('Load time: ',toc-tic, ' seconds')
    
    # helper to convert to parquet
    #convert_xlsx_to_parquet(path)
    pq_path = (path[:-4])+"parquet"
    df.to_parquet(pq_path)
    
    return df

def import_SDGdata_parquet(path, cunts):
    # loads local .xls SDG development goals, cleans and returns dataframe
    print("Loading data: ", path)    
    tic = time.perf_counter()
    
    df = pd.read_parquet(path)   
    #df.columns=["m49_un_a3", "Country", "Year", "Series", "Value", "Note", "Source"]
            
    # concatenate the goal/target/indicator to source
    df['curatedSrc'] = 'United Nations Sustainable Development Goals (SDG) Indicators Database. '
    df['goalid']=' Goal '
    df['targetid']=' Target '
    df['indicatorid']=' Indicator '
    df['seriesid']=' Series ID: '   
    df['newSource'] = df['curatedSrc'] + df['Source'] + df['goalid'] + df['Goal'].astype(str) + df['targetid'].astype(str) + df['Target'].astype(str) + df['indicatorid'] + df['Indicator'] + df['seriesid'] + df['SeriesCode'] 
    
    #drop unneeded columns
    df = df.drop(columns=['goalid','targetid','indicatorid','seriesid','Source','Goal','Target','Indicator','SeriesCode'])
    df = df.rename(columns={"newSource":"Source"})
    
    # organise cols
    df = df[["GeoAreaCode", "GeoAreaName", "TimePeriod", "SeriesDescription", "Value", "FootNote", "Source" ]]
    
    # rename cols
    df = df.rename(columns={"GeoAreaCode":'m49_un_a3', "GeoAreaName":'Country', "TimePeriod":'Year', "SeriesDescription":'Series', "FootNote":'Note'})
    
    #padd the 3 digit m49 country integer with zeros if it less than 100 (i.e. "3" will become "003")    
    df['m49_un_a3'] = df['m49_un_a3'].astype(str).str.zfill(3) 
    
    #strip out any non-country regions from the dataset, based on cunts shortlist
    df = df[df['m49_un_a3'].isin(cunts['m49_a3_country'])]   
    
    #drop any rows with nan value
    print("pre nan len", len(df))
    df = df.dropna(subset=['Value'])
    print("post nan len", len(df))
    
    #cast to strings
    df['Value'] = df['Value'].astype(str)
    df['Year'] = df['Year'].astype(str)
    
    #summary 
    print(pd.unique(df['Series']))
    print(len(pd.unique(df['Series'])), " unique series.")  
    
    #helper to save unique series, note, source -> dataset_lookup
    #df.drop_duplicates(['Series']).to_csv('sdg.csv')
    
    # drop the note, source cols
    df = df.drop(columns=['Note','Source'])
    
    #remove any commas from the value common before casting it
    df["Value"] = df["Value"].str.replace(',','')
    
    toc = time.perf_counter()    
    print('Load time: ',toc-tic, ' seconds')    
 
    
    return df


def import_UNdata_parquet(path, cunts):
    # loads a local datafram from CSV, cleans, and returns dataframe (this function needs to be generalised)
    
    print("Loading data: ", path)    
    
    tic = time.perf_counter()
    
    p = pd.read_parquet(path)
    
    # rename columns
    p.columns=["m49_un_a3", "Country", "Year", "Series", "Value", "Note", "Source"]
    
    # delete first 2 rows
    p = p.iloc[
        2:,
    ]
    
    #remove any commas from the value common before casting it
    p["Value"] = p["Value"].str.replace(',','')
    
    # cast value to a proper float point (as it is string at moment)
    p["Value"] = p["Value"].astype(float)    
    
    #padd the 3 digit m49 country integer with zeros if it less than 100 (i.e. "3" will become "003")
    p['m49_un_a3'] = p['m49_un_a3'].str.zfill(3)  
    
    #loop through and remove any series/year combinations where the count is less than 150
    p = p.groupby(['Series', 'Year'], as_index=False).apply(lambda x: x if len(x) > 150 else pd.DataFrame())   
        
    #strip out any non-country regions from the dataset, based on cunts shortlist
    p = p[p['m49_un_a3'].isin(cunts['m49_a3_country'])]    
    
    #helper to save unique series, note, source -> dataset_lookup
    #p.drop_duplicates(['Series']).to_csv(series+'_unique.csv')
    
    # drop the note, source cols
    p = p.drop(columns=['Note','Source'])    

    toc = time.perf_counter()    
    print('Load time: ',toc-tic, ' seconds')    
    
    return p



def import_UNdata_csv(path, cunts):
    # loads a local datafram from CSV, cleans, and returns dataframe (this function needs to be generalised)
    
    print("Loading data: ", path)    
    
    tic = time.perf_counter()
    
    # import UN population data and clean ready for choropleth
    p = pd.read_csv(
        path,
        encoding="latin-1",
        names=["m49_un_a3", "Country", "Year", "Series", "Value", "Note", "Source"],
    )  
    
    # delete first 2 rows
    p = p.iloc[
        2:,
    ]
    
    #remove any commas from the value common before casting it
    p["Value"] = p["Value"].str.replace(',','')
    
    # cast value to a proper float point (as it is string at moment)
    p["Value"] = p["Value"].astype(float)    
    
    #padd the 3 digit m49 country integer with zeros if it less than 100 (i.e. "3" will become "003")
    p['m49_un_a3'] = p['m49_un_a3'].str.zfill(3)  
    
    #loop through and remove any series/year combinations where the count is less than 150
    p = p.groupby(['Series', 'Year'], as_index=False).apply(lambda x: x if len(x) > 150 else pd.DataFrame())   
        
    #strip out any non-country regions from the dataset, based on cunts shortlist
    p = p[p['m49_un_a3'].isin(cunts['m49_a3_country'])]    
    
    #helper to save unique series, note, source -> dataset_lookup
    #p.drop_duplicates(['Series']).to_csv(series+'_unique.csv')
    
    # drop the note, source cols
    p = p.drop(columns=['Note','Source'])    

    toc = time.perf_counter()    
    print('Load time: ',toc-tic, ' seconds')
    
    # helper to convert
    #convert_csv_to_parquet(path)
    
    return p

def import_discrete_data(path, cunts):
    print("Loading data: ", path)
    
    # import standard csv structure
    p = pd.read_csv(
        path,
        encoding="latin-1",
        names=["m49_un_a3", "Country", "Year", "Series", "Value", "Note", "Source"],
    )
    
    # delete first row (column headings)
    p = p.iloc[ 1:,]
    
    #padd the 3 digit m49 country integer with zeros if it less than 100 (i.e. "3" will become "003")
    p['m49_un_a3'] = p['m49_un_a3'].str.zfill(3)  
    
    # drop the note, source cols
    p = p.drop(columns=['Note','Source'])
    
    return p


def add_regions(df, cunts):
    
    print('Adding regions ...')
    tic = time.perf_counter()
    
    df['continent'] = "testing"
    df['region_un'] = "testing"
    df['region_wb'] = "testing"
    
    #loop through all unique countries
    for i in cunts['m49_a3_country']:               
        
        #set the regions for each unique country to columns in the master df
        try:
            df.loc[df['m49_un_a3']==i, 'continent'] = cunts.loc[cunts['m49_a3_country'] == i].iloc[0,2]
            df.loc[df['m49_un_a3']==i, 'region_un'] = cunts.loc[cunts['m49_a3_country'] == i].iloc[0,3]
            df.loc[df['m49_un_a3']==i, 'region_wb'] = cunts.loc[cunts['m49_a3_country'] == i].iloc[0,4]
        
        except KeyError as error:
            print("add_regions: Exception thrown")        
    
    toc = time.perf_counter()    
    print('Load time ',toc-tic, ' seconds')
        
    return    


def get_regions(cunts,gj):
    
    #this is a helper function where I extracted the regions from the json data, and exported it to csv to replace m49 starter file.    
    #create cols
    cunts['continent'] = "No continent"
    cunts['region_un'] = "No region"
    cunts['region_wb'] = "No subregion"
    
    for i in range(0, len(gj['features'])):
        try:
                        
            continent = gj['features'][i]['properties']['continent']
            region_un = gj['features'][i]['properties']['region_un']
            region_wb = gj['features'][i]['properties']['region_wb']
            m49_json = gj['features'][i]['properties']['un_a3']
            
            #set deets
            cunts.loc[cunts.m49_a3_country == m49_json, 'continent'] = continent
            cunts.loc[cunts.m49_a3_country == m49_json, 'region_un'] = region_un
            cunts.loc[cunts.m49_a3_country == m49_json, 'region_wb'] = region_wb
            
            #print(continent)
            #print(region_un)
            #print(region_wb)      
        
        except IndexError as error:
            print("add_regions: Exception thrown attempting to build custom dict from json (expected)")
    
    #print(cunts)
    #cunts.to_csv(r'C:\Users\Dan\Documents\GitHub\atlas\data\experimental\cunts.csv', index = False)    
           
    return



    

def create_unique_country_list(path):
    
    #read in m49 codes from csv
    c =  pd.read_csv(
       path,
       encoding="utf-8",
       names=["m49_a3_country", "country", "continent", "region_un", "region_wb", "su_a3"],
    )
    
    #cast to string
    c["m49_a3_country"] = c["m49_a3_country"].astype(str) 
    
    #padd the 3 digit m49 country integer with zeros if it less than 100 (i.e. "3" will become "003")
    c['m49_a3_country'] = c['m49_a3_country'].str.zfill(3)  
    
    # delete first row (column headings)
    c = c.iloc[1:,]
    
    return c


def add_su_a3(country_lookup, gj):
    #Helper function. Not needed anymore.    
    
    c = copy.deepcopy(country_lookup)
    
    c['SU_A3'] = ""
    
    #loop through the json and add to country_lookup if posible    
    for i in range(0, len(gj['features'])):
        if gj['features'][i]['properties']['UN_A3'] in c["m49_a3_country"].values:
            c.loc[c.m49_a3_country == gj['features'][i]['properties']['UN_A3'], 'SU_A3'] = gj['features'][i]['properties']['SU_A3']
            #print(i)
        
        
    #if all works, export to .csv, then look at permanently fixing the globe json too
    c.to_csv(r'C:\Users\Dan\Documents\GitHub\atlas\data\experimental\testingstuff.csv', index = False)  
    
    return c


def create_dataset_lookup(path):
    
    #read in lookup table of raw datasets and their labels
    d= pd.read_csv(
       path,
       encoding="utf-8",
       names=["dataset_id", "dataset_raw", "dataset_label", "source", "link", "var_type", "nav_cat", "colour", "nav_cat_nest", "tag1", "tag2", "explanatory_note"],
    )
    
    # delete first 1 rows (col headers)
    d = d.iloc[1:,] 
    
    #d['explanatory_note'] = d['explanatory_note'].fillna('')
    
    
        
    return d


def get_source(ds_lookup, series):    
    
    source = ds_lookup[ds_lookup['dataset_raw']==series].iloc[0]['source']
       
    return source
  
def get_link(ds_lookup, series):    
    
    link = ds_lookup[ds_lookup['dataset_raw']==series].iloc[0]['link']
       
    return link
  
       
def check_year(pop, series, year):
           
    # get unique years from series
    df = pop.loc[(pop['Series'] == series)]
    
    # convert to list
    years = pd.DataFrame(pd.unique(df["Year"]), columns=["value"])['value'].tolist()
           
    # return bool if year found
    return int(year) in years
    

def get_years(df):
    # strip out years from dataset and return as dictionary (for control input)
    df = df.sort_values('Year')
    years = pd.DataFrame(pd.unique(df["Year"]), columns=["value"])
    years = years["value"].to_dict()
    #print(years)
    return years


def get_year_slider_index(pop, series, year):
    
    #obtain relevant years for this series
    yr_slider = get_years(pop.loc[(pop['Series'] == series)])
        
    if len(yr_slider) > 0:
        for index in range(len(yr_slider)):  
            if yr_slider[index] == year: return index
            
    #otherwise return most recent    
    return len(yr_slider)-1


def get_year_slider_marks(series, pop, INIT_YEAR_SLIDER_FONTSIZE, INIT_YEAR_SLIDER_FONTCOLOR, year_slider_selected):    
    
    #obtain relevant years for this series and update slider
    year_slider_marks = get_years(pop.loc[(pop['Series'] == series)])
    
    # add styling to year slider        
    year_slider_marks2 = {
                    i: {
                        "label": year_slider_marks[i],
                        "style": {"fontSize": INIT_YEAR_SLIDER_FONTSIZE, 'color':INIT_YEAR_SLIDER_FONTCOLOR, 'fontWeight': 'normal'},
                    }
                    for i in range(0, len(year_slider_marks))
                }   
    
    year_slider_marks=year_slider_marks2     
     
    # shorten year labels if needed
    
    #10-20 = '91 style
    #if len(year_slider_marks) > 10 and len(year_slider_marks) <= 20:
    #    for i in range(0,len(year_slider_marks)):
    #        year_slider_marks[i]['label'] = "'"+str(year_slider_marks[i]['label'])[2:]
    #        #year_slider_marks[i]['style']['fontSize']=12
    
    
    #10-20 = '91 style
    if len(year_slider_marks) > 10 and len(year_slider_marks) <= 20:
        counter = 0
        for i in range(0,len(year_slider_marks)):   
            if i == 0 or i == len(year_slider_marks)-1:              
                continue    
            if counter != 1:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
    
    
    
    #20-50 = every 5 yrs
    elif len(year_slider_marks) > 20 and len(year_slider_marks) <= 50:                    
        counter = 0
        for i in range(0,len(year_slider_marks)):   
            if i == 0 or i == len(year_slider_marks)-1:              
                continue    
            if counter != 4:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
                
    #50-100 = every 10 yrs
    elif len(year_slider_marks) > 50 and len(year_slider_marks) <= 100:                      
        counter = 0
        for i in range(0,len(year_slider_marks)):  
            if i == 0 or i == len(year_slider_marks)-1:              
                continue   
            if counter != 9:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
                
    #100-200 = every 20 yrs
    elif len(year_slider_marks) > 100 and len(year_slider_marks) <= 200:                      
        counter = 0
        for i in range(0,len(year_slider_marks)): 
            if i == 0 or i == len(year_slider_marks)-1:              
                continue 
            if counter != 19:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
    
    #200+ = every 50 yrs
    elif len(year_slider_marks) > 200:                      
        counter = 0
        for i in range(0,len(year_slider_marks)):  
            if i == 0 or i == len(year_slider_marks)-1:              
                continue   
            if counter != 49:
                year_slider_marks[i]['label'] = ""               
                counter = counter + 1
            else:                
                counter = 0
    
    
    
    return year_slider_marks




def get_series_and_year(df, year, series, ascending):
    #print("Get series. Year %r, series %r, ascending %r", year, series, ascending)
    
    #Subset main dataframe for this series and year as a shallow copy (so we can cast value to Float)
    d = copy.copy(df[(df["Year"] == int(year)) & (df["Series"] == series)]) #This could be a memory leak, or at least seems inefficient.
    
    d['Value'] = d['Value'].astype(float) 
    
    # dropping ALL duplicate values (THIS SHOULDNT BE NEEDED BUT SOME DATASETS MAY BE A LITTLE CORRUPTED. E.g 'Annual mean levels of fine particulate matter in cities, urban population (micrograms per cubic meter)'
    d = d.drop_duplicates(subset ="m49_un_a3")

    d = d.sort_values('Value', ascending=ascending)
    return d

def get_series(df, series, ascending):
    #print("Get series. Series %r, ascending %r", series, ascending)
    d = copy.copy(df[(df["Series"] == series)])
    d['Year'] = d['Year'].astype(int)
    d['Value'] = d['Value'].astype(float)
    d = d.sort_values('Value', ascending=ascending)
    return d



def load_geo_data_JSON(json_path):    
    '''
    #logger.info("Load geo data method called, attempting to load new polygon dataset")
    with open(json_path, "r") as read_file:
        countries_json = json.load(read_file)'''
    
    #with open(json_path, encoding='utf-8') as read_file:
    #    countries_json = json.load(read_file)
    
    countries_json = json.load(open(json_path, 'r', encoding='utf-8'))
    
    return countries_json

def clean_3d_land_data_JSON_ne110m(json_path):
    
    #this dataset does in fact have the integer codes we want, so all we need to do is some basic processing to make it consistent with what is expected by update_3d_geo_data_JSON
    #i.e. add a few properties with consistent names to what is used in the ne50m data
    #these clean functions are helpers, they only really need to be run once, to producea cleaned geojson file for importing at runtime.
    
    #load data    
    countries_json = json.load(open(json_path, 'r', encoding='utf-8'))
    
    #bring country name up to feature level (from properties.) This is required for tooltip to work on deck.gl    
    gj = copy.deepcopy(countries_json)
    
    #add country name and random colours
    for i in range(0, len(gj['features'])):
        gj['features'][i]['COUNTRY'] = gj['features'][i]['properties']['SUBUNIT'] #grab country name from json(this fieldname differs between natural earth datasets)
        gj['features'][i]['properties']['red']= np.random.randint(0,255)
        gj['features'][i]['properties']['green']= np.random.randint(0,255)
        gj['features'][i]['properties']['blue']= np.random.randint(0,255)
    
    #now we simply create a new property 'sr_un_a3' for consistency with the other datasets so all functions work. In this case, we'll duplicate ISO_n3
    for i in range(0, len(gj['features'])):
        gj['features'][i]['properties']['sr_un_a3'] = gj['features'][i]['properties']['ISO_N3']
    
    
    #now try to write the json as a once off and test it.       
    with open('data/geojson/globe/ne_110m_land_test.geojson', 'w') as outfile:
        json.dump(gj, outfile) 
    
    return gj


def clean_3d_land_data_JSON_ne50m(json_path, cunts):    
    
    #This dataset does NOT have the unique integer codes for which I've used as the primary key to extract from pop when updating (in another func)
    #consequently I've added alphanumeric codes "AUS" to the country_lookup, then extracted the integer code and added it to this json under 'sr_un_a3'
    
    #load data    
    countries_json = json.load(open(json_path, 'r', encoding='utf-8'))
            
    #bring country name up to feature level (from properties.) This is required for tooltip to work on deck.gl    
    gj = copy.deepcopy(countries_json)
    
    #add country name and random colours
    for i in range(0, len(gj['features'])):
        gj['features'][i]['COUNTRY'] = gj['features'][i]['properties']['sr_subunit'] #grab country name from json  
        gj['features'][i]['properties']['red']= np.random.randint(0,255)
        gj['features'][i]['properties']['green']= np.random.randint(0,255)
        gj['features'][i]['properties']['blue']= np.random.randint(0,255)
  
    #add in the un_a3 integer code (once) and test out writing this file
    for i in range(0, len(gj['features'])):
        #print(gj['features'][i]['properties']['sr_su_a3'])
        
        if gj['features'][i]['properties']['sr_adm0_a3'] in cunts['su_a3'].values:
            #extract un_a3 integer code from lookup and set it as a new feature property in the json
            gj['features'][i]['properties']['sr_un_a3'] = cunts[cunts["su_a3"]==gj['features'][i]['properties']['sr_adm0_a3']].iloc[0,0]
        else:            
            gj['features'][i]['properties']['sr_un_a3'] = "none"
            
    #now try to write the json as a once off and test it.       
    with open('data/geojson/globe/ne_50m_land_test.geojson', 'w') as outfile:
        json.dump(gj, outfile)    
             
    return gj

def load_3d_geo_data_JSON_cleaned(json_path):    
    #load data    
    gj = json.load(open(json_path, 'r', encoding='utf-8'))
    return gj

def clean_3d_ocean_data_JSON_ne110m(json_path):
    
    #load raw json
    geojson_globe_ocean_ne50m = json.load(open(json_path, 'r', encoding='utf-8'))
    
    #deep copy json (had problems so this works)    
    ocean_coords = copy.deepcopy(geojson_globe_ocean_ne50m)

    #geojson_globe_ocean_ne50m_test = d.load_3d_geo_data_JSON_cleaned("data/geojson/globe/ne_50m_ocean.geojson")
    
    #del(ocean_coords['features'][0]['geometry']['coordinates'][1][98])
    
    '''
    #convert ocean multipolygon feature collection (from natural earth) into single polygon shape, for parsing by deck.gl
    mp = geometry.as_shape(geojson_globe_ocean_ne50m['features'][0]['geometry']) #yields two element polygon set
    coord1 = mp.geoms[0].__geo_interface__['coordinates'] #Caspian sea
    coord2 = mp.geoms[1].__geo_interface__['coordinates'] #Ocean
    
    #convert the tuples of coordinates into lists at all levels (3 levels deep)
    coord1_L = list(copy.deepcopy(coord1))
    for i in range(0, len(coord1_L)):    
        coord1_L[i] = list(coord1_L[i])
        for j in range(0, len(coord1_L[i])):
            coord1_L[i][j] = list(coord1_L[i][j])
    
    coord2_L = list(copy.deepcopy(coord2))
    for i in range(0, len(coord2_L)):    
        coord2_L[i] = list(coord2_L[i])
        for j in range(0, len(coord2_L[i])):
            coord2_L[i][j] = list(coord2_L[i][j])
    
    #THIS IS IMPORTANT AND LIKELY CAUSING THE GLITCHYNESS OVER AMERICAS
    del(coord2_L[98]) #this set of 9000 points cause noload. Not sure why, but it is americas, in main ocean file
    '''
    
    #ocean: add json features
    geojson_globe_ocean_ne50m['features'][0]['properties']['sr_un_a3'] = "000" 
    geojson_globe_ocean_ne50m['features'][0]['COUNTRY'] = "Ocean"
    geojson_globe_ocean_ne50m['features'][0]['geometry']['type'] = "Polygon"
    #geojson_globe_ocean_ne50m['features'][0]['geometry']['coordinates'] = coord2_L
    geojson_globe_ocean_ne50m['features'][0]['geometry']['coordinates'] = ocean_coords['features'][1]['geometry']['coordinates'][0] 
    
    #append a duplicate of this dictionary to list (i.e. because it was not read in from file like this)
    #geojson_globe_ocean_ne50m['features'].append(copy.deepcopy(geojson_globe_ocean_ne50m['features'][0]))
    
    #Caspian sea: add json features
    geojson_globe_ocean_ne50m['features'][1]['properties']['sr_un_a3'] = "000" #must add this custom property to json
    geojson_globe_ocean_ne50m['features'][1]['COUNTRY'] = "Caspian Sea"
    geojson_globe_ocean_ne50m['features'][1]['geometry']['type'] = "Polygon"
    #geojson_globe_ocean_ne50m['features'][1]['geometry']['coordinates'] = coord1_L
    geojson_globe_ocean_ne50m['features'][1]['geometry']['coordinates'] = ocean_coords['features'][0]['geometry']['coordinates'][0] #caspian sea
    
    #now try to write the json as a once off and test it.       
    gj = geojson_globe_ocean_ne50m
    with open('data/geojson/globe/ne_110m_ocean_test.geojson', 'w') as outfile:
        json.dump(gj, outfile) 
    
    return geojson_globe_ocean_ne50m



def clean_3d_ocean_data_JSON_ne50m(json_path):
    
    #load raw json
    geojson_globe_ocean_ne50m = json.load(open(json_path, 'r', encoding='utf-8'))
    
    #deep copy json (had problems so this works)    
    ocean_coords = copy.deepcopy(geojson_globe_ocean_ne50m)

    #geojson_globe_ocean_ne50m_test = d.load_3d_geo_data_JSON_cleaned("data/geojson/globe/ne_50m_ocean.geojson")
    
    del(ocean_coords['features'][0]['geometry']['coordinates'][1][98])
    
    '''
    #convert ocean multipolygon feature collection (from natural earth) into single polygon shape, for parsing by deck.gl
    mp = geometry.as_shape(geojson_globe_ocean_ne50m['features'][0]['geometry']) #yields two element polygon set
    coord1 = mp.geoms[0].__geo_interface__['coordinates'] #Caspian sea
    coord2 = mp.geoms[1].__geo_interface__['coordinates'] #Ocean
    
    #convert the tuples of coordinates into lists at all levels (3 levels deep)
    coord1_L = list(copy.deepcopy(coord1))
    for i in range(0, len(coord1_L)):    
        coord1_L[i] = list(coord1_L[i])
        for j in range(0, len(coord1_L[i])):
            coord1_L[i][j] = list(coord1_L[i][j])
    
    coord2_L = list(copy.deepcopy(coord2))
    for i in range(0, len(coord2_L)):    
        coord2_L[i] = list(coord2_L[i])
        for j in range(0, len(coord2_L[i])):
            coord2_L[i][j] = list(coord2_L[i][j])
    
    #THIS IS IMPORTANT AND LIKELY CAUSING THE GLITCHYNESS OVER AMERICAS
    del(coord2_L[98]) #this set of 9000 points cause noload. Not sure why, but it is americas, in main ocean file
    '''
    
    #ocean: add json features
    geojson_globe_ocean_ne50m['features'][0]['properties']['sr_un_a3'] = "000" 
    geojson_globe_ocean_ne50m['features'][0]['COUNTRY'] = "Ocean"
    geojson_globe_ocean_ne50m['features'][0]['geometry']['type'] = "Polygon"
    #geojson_globe_ocean_ne50m['features'][0]['geometry']['coordinates'] = coord2_L
    geojson_globe_ocean_ne50m['features'][0]['geometry']['coordinates'] = ocean_coords['features'][0]['geometry']['coordinates'][1] #main ocean
    
    #append a duplicate of this dictionary to list (i.e. because it was not read in from file like this)
    geojson_globe_ocean_ne50m['features'].append(copy.deepcopy(geojson_globe_ocean_ne50m['features'][0]))
    
    #Caspian sea: add json features
    geojson_globe_ocean_ne50m['features'][1]['properties']['sr_un_a3'] = "000" #must add this custom property to json
    geojson_globe_ocean_ne50m['features'][1]['COUNTRY'] = "Caspian Sea"
    geojson_globe_ocean_ne50m['features'][1]['geometry']['type'] = "Polygon"
    #geojson_globe_ocean_ne50m['features'][1]['geometry']['coordinates'] = coord1_L
    geojson_globe_ocean_ne50m['features'][1]['geometry']['coordinates'] = ocean_coords['features'][0]['geometry']['coordinates'][0] #caspian sea
    
    #now try to write the json as a once off and test it.       
    gj = geojson_globe_ocean_ne50m
    with open('data/geojson/globe/ne_50m_ocean_test.geojson', 'w') as outfile:
        json.dump(gj, outfile) 
    
    return geojson_globe_ocean_ne50m


def update_3d_geo_data_JSON(df, geojson, colorscale, jellybean, var_type, discrete_colorscale):
    #update a copy of the geojson data to include series specific data from the passed in dataframe (subset) including label names, and colours
        
    #FIRST DO THE COLOUR INTERPOLATION
    
    #fix for removing note and source columns
    df['fix1'] = "dummmy"
    df['fix2'] = "dummy"
    
    #For continuous data we'll do linear color interpolation based on the extracted colorscale from the main map
    if var_type == "continuous" or var_type == "ratio" or var_type == "quantitative":
    
        #cast values to float
        df['Value'] = df['Value'].astype(float)  
        
        #drop values below zero (they cannot be displayed on current choropleth style)
        df = df[df.Value > 0]  
        
        #transform the data values to log10 (zeros introduced where log not computed)
        df['value_log10'] = np.log10(df['Value'], out=np.zeros_like(df['Value']), where=(df['Value']!=0))        
        
        #now drop any rows with zero vals (or it will be affected by subsequent colour interpolation logic)
        df = df[df.value_log10 != 0]       
        
        #translate data range to positive
        mn = np.min(df["value_log10"])
        mx = np.max(df["value_log10"])
        if mn < 0.0:            
            #print("Color correction, translating log vals")
            df['value_log10'] = df['value_log10'] + abs(mn)
        
        #now calculate the 0-1 ratio (normalise)
        df['f-log'] = df['value_log10'] / np.max(df["value_log10"]) #i.e. what proportion is it of the max   
        
        #get colorscale array from mapdata (this is variable length and can switch to RGB from Hex)
        #colorscale = map_data['data'][0]['colorscale'] #an list of colours e.g. [1.1111, #hexcolour]   
        
        if colorscale[0][1][0] != "#":
            #i.e. we have an RGB color array (happens after settings are changed), so convert to hex
            #print("RGB color array found in map data. Converting to hex")
            for i in range(0,len(colorscale)):              
                red = extractRed(colorscale[i][1])
                green = extractGreen(colorscale[i][1])
                blue = extractBlue(colorscale[i][1])
                hx = '#{:02x}{:02x}{:02x}'.format(red, green , blue)
                #print(red, green, blue, hx)
                colorscale[i][1] = hx #replace rgb string with hex string
        
        #print(df['f-log'])
        #print(colorscale)
        
        #based on the value for each row, obtain the two colours and mixing to interpolate between them!
        df['c1'] = df.apply(lambda row : extractColorPositions(colorscale, row['f-log'])[0], axis =1).astype(str)
        df['c2'] = df.apply(lambda row : extractColorPositions(colorscale, row['f-log'])[1], axis =1).astype(str)
        df['mix'] = df.apply(lambda row : extractColorPositions(colorscale, row['f-log'])[2], axis =1).astype(float)
        
        #get hex val by linear interpolation between c1, c2, mix for each row, and also convert this into the component RGB vals (for deck.gl)
        df['hex'] = df.apply(lambda row : colorFader(row['c1'], row['c2'], row['mix']), axis =1) #linear interpolation between two hex colours
        
        df['r'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[0], axis =1).astype(str) #return the red (index 0 of tuple) from the RGB tuble returned by getcolor 
        df['g'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[1], axis =1).astype(str) #return the greeen (index 0 of tuple) from the RGB tuble returned by getcolor 
        df['b'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[2], axis =1).astype(str) #return the blue (index 0 of tuple) from the RGB tuble returned by getcolor 
          
        #print(df.columns)
        #print(colorscale)
    
    #For discrete data, set colour scales based on global lookup
    elif var_type == "discrete":                
        
        #mimic the same df structure as the continuous dataset, so the logic further below works (creating dummy columns)
        df['value_log10'] = "dummy"
        df['f-log'] = "dummy"
        df['c1'] = "dummy"
        df['c2'] = "dummy"
        df['mix'] = "dummy"
        df['hex'] = "dummy"  
        
        #obtain array of discrete categories
        discrete_cats = pd.unique(df['Value'])
       
        #loop through unique discrete categories and set the hex value based on discrete colour scale lookup
        for i in range(0,len(discrete_cats)):                    
            df.loc[df['Value']==discrete_cats[i], 'hex'] = discrete_colorscale[i][0][1]
        
        #Convert the hex value to separate R/G/B values as cols, as this data is needed by pdeck to render the globe        
        df['r'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[0], axis =1).astype(str) #return the red (index 0 of tuple) from the RGB tuble returned by getcolor 
        df['g'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[1], axis =1).astype(str) #return the greeen (index 0 of tuple) from the RGB tuble returned by getcolor 
        df['b'] = df.apply(lambda row : ImageColor.getcolor(row['hex'], "RGB")[2], axis =1).astype(str) #return the blue (index 0 of tuple) from the RGB tuble returned by getcolor 
    
    
    #NOW ADD COLOUR AND SERIES SPECIFIC DATA TO GEOJSON
    
    #deep copy globe geojson
    gj = copy.deepcopy(geojson)
   
    #loop through all 1300 geojson features and set the value based on current series
    for i in range(0, len(gj['features'])):
        try:                               
            
            #At this point, check if country name/val None (i.e. no data in DF), and grab the country name for the properties of the JSON, and set the value to 0            
            #if no data exists for a country in this series, store the country name from json, set val to 0, and set a nice grey colour so it displays on jigsaw
            if gj['features'][i]['properties']['sr_un_a3'] not in df["m49_un_a3"].values:
                #print(gj['features'][i]['properties']['BRK_NAME'])
                #gj['features'][i]['COUNTRY'] = gj['features'][i]['properties']['BRK_NAME'] #grab country name from json              
                gj['features'][i]['VALUE'] = "no data"                    
                
                #Colour ocean blue
                if gj['features'][i]['COUNTRY'] == "Ocean" or gj['features'][i]['COUNTRY'] == "Caspian Sea":
                    gj['features'][i]['properties']['red'] = "134" #ocean blue
                    gj['features'][i]['properties']['green'] = "181"
                    gj['features'][i]['properties']['blue'] = "209"
                
                #Colour all other features missing data as grey
                else:
                    gj['features'][i]['properties']['red'] = "224" #grey
                    gj['features'][i]['properties']['green'] = "224"
                    gj['features'][i]['properties']['blue'] = "224"
                
            else:             
                #set value of current series to this row item in json               
                gj['features'][i]['VALUE'] = df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,4] #set geojson property to the value of the series for that country
                
                #colour the feature for this country based on the interpolated colours
                if jellybean == False:
                    gj['features'][i]['properties']['red']= df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,16]
                    gj['features'][i]['properties']['green']= df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,17]
                    gj['features'][i]['properties']['blue']= df[df["m49_un_a3"]==gj['features'][i]['properties']['sr_un_a3']].iloc[0,18]
         
        except IndexError as error:
            print("Globe: Exception thrown attempting to build custom dict from json (expected)")
         
    
    return gj



def colorFader(c1,c2,mix=0): 
    #fade (linear interpolate) from color c1 (at mix=0) to c2 (mix=1)
    #c1 and c2 are hex colours, mix variable is a float point between 0 and 1, and colour will be interpolated and a hex colour will be returned
    c1=np.array(mpl.colors.to_rgb(c1))
    c2=np.array(mpl.colors.to_rgb(c2))
    return mpl.colors.to_hex((1-mix)*c1 + mix*c2)
   
def extractRed(rgb_str):
    #rip out the red    
    r = rgb_str.split(",")
    red = r[0].strip("rgb() ") #select red val from the array, and remove zeros    
    return int(red)


def extractGreen(rgb_str):
    #rip out the green    
    g = rgb_str.split(",")
    green = g[1].strip() #select red val from the array, and remove zeros    
    return int(green)
    
def extractBlue(rgb_str):
    #rip out the blue
    b = rgb_str.split(",")
    blue = b[2].strip("() ") #select red val from the array, and remove zeros    
    return int(blue)

def extractColorPositions(colorscale, val):
    #this function takes the given colour array and a value, and returns the respective c1, c2, mix vars needed for linear colour interpolation

    colorscale_r = copy.deepcopy(colorscale)
    
    #reverse colorscale
    for i in range(0, len(colorscale)):        
        colorscale_r[(len(colorscale)-1)-i][1] = colorscale[i][1]
    
    colorscale = copy.deepcopy(colorscale_r)
    
    #Find the val position in the colour scale, store the two colours and the mix level to interpolate between them based on val
    for i in range(0, len(colorscale)-1):    
        
        if val <= colorscale[i+1][0]:
            c1 = colorscale[i][1]
            c2 = colorscale[i+1][1]
            mix = (val - colorscale[i][0]) / (colorscale[i+1][0] - colorscale[i][0])    
            #print(c1)
            #print(c2)
            #print(mix)
            return c1, c2, mix
    return    
    
def helper_prepare_explanatory_notes_for_source():
    # this doesn't get called, usually just executed manually for cleaning jobs. Saved here so as not to be lost    

    #Load master lookup table to link raw datasets to a label
    dataset_lookup = create_dataset_lookup("data/dataset_lookup.csv")
    
    ds = copy.deepcopy(dataset_lookup)
    
    #fix fastrack indicators    
    fastrack = pd.read_csv('gapminder_source_fasttrack_helper.csv')
      
    for i in fastrack['Series']:     
        try:
            ds.loc[ds['dataset_raw']==i, 'source'] = fastrack.loc[fastrack['Series'] == i].iloc[0,6]
            ds.loc[ds['dataset_raw']==i, 'link'] = fastrack.loc[fastrack['Series'] == i].iloc[0,7]
            ds.loc[ds['dataset_raw']==i, 'explanatory_note'] = fastrack.loc[fastrack['Series'] == i].iloc[0,8]
            print('fixed')
        
        except KeyError as error:
            print("Exception thrown")        
        
    # now system globalis
    fastrack = pd.read_csv('gapminder_systglob_source_helper.csv')
    for i in fastrack['Series']:     
        try:
            ds.loc[ds['dataset_raw']==i, 'source'] = fastrack.loc[fastrack['Series'] == i].iloc[0,6]
            ds.loc[ds['dataset_raw']==i, 'link'] = fastrack.loc[fastrack['Series'] == i].iloc[0,7]
            ds.loc[ds['dataset_raw']==i, 'explanatory_note'] = fastrack.loc[fastrack['Series'] == i].iloc[0,8]
            print('fixed')
        
        except KeyError as error:
            print("Exception thrown")         
     
    # now would dev
    fastrack = pd.read_csv('gapminder_worlddev_source_helper.csv')
    for i in fastrack['Series']:     
        try:
            ds.loc[ds['dataset_raw']==i, 'source'] = fastrack.loc[fastrack['Series'] == i].iloc[0,6]
            ds.loc[ds['dataset_raw']==i, 'link'] = fastrack.loc[fastrack['Series'] == i].iloc[0,7]
            ds.loc[ds['dataset_raw']==i, 'explanatory_note'] = fastrack.loc[fastrack['Series'] == i].iloc[0,8]
            print('fixed')
        
        except KeyError as error:
            print("Exception thrown")   
    
    #pad nans with a message
    ds['explanatory_note'] = ds['explanatory_note'].fillna('No extra information is available for this dataset.')
    
    # dump back to csv
    ds.to_csv('dataset_lookup_special.csv')    

    return