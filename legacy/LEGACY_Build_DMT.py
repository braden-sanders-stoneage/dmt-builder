# %%
import pandas as pd
import os

# %%
def create_directory():
    
    directory = input()
    return os.path.normpath(directory)

# %%
def create_filepath(directory):
    
    print('Please input your desired filename:')
    filename = input()
    print('~~~~~~~~~~~~~~~~~~~')
    print('Thanks! Filename Recorded.')
    filepath = os.path.join(directory, filename + '.xlsx')
    print('~~~~~~~~~~~~~~~~~~~')
    print('FILEPATH:')
    print(filepath)
    print('~~~~~~~~~~~~~~~~~~~')
    
    return filename,filepath

# %%
def build_UD11(filepath):
    
    UD11_df = pd.read_excel(filepath)
    UD11_df.columns = ['Company', 'Key1','Key2','Key3','Key4','Key5']
    
    UD11_companylist = UD11_df['Company'].tolist()
    UD11_key1list = UD11_df['Key1'].tolist()
    UD11_key2list = UD11_df['Key2'].tolist()
    UD11_key3list = UD11_df['Key3'].tolist()
    UD11_key4list = UD11_df['Key4'].tolist()
    UD11_key5list = UD11_df['Key5'].tolist()
    
    return UD11_df,UD11_companylist,UD11_key1list,UD11_key2list,UD11_key3list,UD11_key4list,UD11_key5list

# %%
def build_variant(UD11_companylist,UD11_key1list,UD11_key2list,UD11_key3list,UD11_key4list,UD11_key5list):
    
    UD10_companylist = []
    UD10_key1list = []
    UD10_key2list = []
    UD10_key3list = []
    UD10_key4list = []
    UD10_key5list = []
    
    UD09_companylist = []
    UD09_key1list = []
    UD09_key2list = []
    UD09_key3list = []
    UD09_key4list = []
    UD09_key5list = []
    
    UD08_companylist = []
    UD08_key1list = []
    UD08_key2list = []
    UD08_key3list = []
    UD08_key4list = []
    UD08_key5list = []
    UD08_character01list = []
    UD08_checkbox01list = []
    
    for index,company in enumerate(UD11_companylist):
        
        key1 = UD11_key1list[index]
        key2 = UD11_key2list[index]
        key3 = UD11_key3list[index]
        key4 = UD11_key4list[index]
        key5 = UD11_key5list[index]
        
        if key5 not in UD10_key4list:
            
            UD10_companylist.append(company)
            UD10_key1list.append(key1)
            UD10_key2list.append(key2)
            UD10_key3list.append(key3)
            UD10_key4list.append(key5)
            
    for index,company in enumerate(UD10_companylist):
    
        key1 = UD10_key1list[index]
        key2 = UD10_key2list[index]
        key3 = UD10_key3list[index]
        
        if key3 not in UD09_key3list:
            
            UD09_companylist.append(company)
            UD09_key1list.append(key1)
            UD09_key2list.append(key2)
            UD09_key3list.append(key3)
    
    for index,company in enumerate(UD09_companylist):
        
        key1 = UD09_key1list[index]
        key2 = UD09_key2list[index]
    
        if key2 not in UD08_key2list:
            
            UD08_companylist.append(company)
            UD08_key1list.append(key1)
            UD08_key2list.append(key2)
            UD08_character01list.append(key2)
            UD08_checkbox01list.append(True)
    
    UD10_dflist = [UD10_companylist,UD10_key1list,UD10_key2list,UD10_key3list,UD10_key4list,UD10_key5list]
    UD10_df_unt = pd.DataFrame(UD10_dflist)
    UD10_df = UD10_df_unt.transpose()
    UD10_df.columns = ['Company', 'Key1','Key2','Key3','Key4','Key5']
    
    UD09_dflist = [UD09_companylist,UD09_key1list,UD09_key2list,UD09_key3list,UD09_key4list,UD09_key5list]
    UD09_df_unt = pd.DataFrame(UD09_dflist)
    UD09_df = UD09_df_unt.transpose()
    UD09_df.columns = ['Company', 'Key1','Key2','Key3','Key4','Key5']
    
    UD08_dflist = [UD09_companylist,UD08_key1list,UD08_key2list,UD08_key3list,UD08_key4list,UD08_key5list,UD08_character01list,UD08_checkbox01list]
    UD08_df_unt = pd.DataFrame(UD08_dflist)
    UD08_df = UD08_df_unt.transpose()
    UD08_df.columns = ['Company', 'Key1','Key2','Key3','Key4','Key5','Character01','Checkbox01']
    
    return UD10_df,UD09_df,UD08_df

# %%
def build_attribute(UD11_companylist,UD11_key1list,UD11_key2list,UD11_key3list):
    
    UD10_companylist = []
    UD10_key1list = []
    UD10_key2list = []
    UD10_key3list = []
    UD10_key4list = []
    UD10_key5list = []
    UD10_character01list = []
    UD10_checkbox01list = []
    
    
    UD09_companylist = []
    UD09_key1list = []
    UD09_key2list = []
    UD09_key3list = []
    UD09_key4list = []
    UD09_key5list = []
    UD09_character01list = []
    UD09_checkbox01list = []
    UD09_checkbox02list = []
    UD09_checkbox03list = []
    UD09_checkbox04list = []
    UD09_checkbox05list = []
    
    for index,company in enumerate(UD11_companylist):
        
        key1 = UD11_key1list[index]
        key2 = UD11_key2list[index]
        key3 = UD11_key3list[index]
        
        if key3 not in UD10_key3list:
            
            UD10_companylist.append(company)
            UD10_key1list.append(key1)
            UD10_key2list.append(key2)
            UD10_key3list.append(key3)
            UD10_character01list.append(key3)
            UD10_checkbox01list.append(True)
    
    for index,company in enumerate(UD10_companylist):
    
        key1 = UD10_key1list[index]
        key2 = UD10_key2list[index]
        
        if key2 not in UD09_key2list:
            
            UD09_companylist.append(company)
            UD09_key1list.append(key1)
            UD09_key2list.append(key2)
            UD09_character01list.append(key2)
            UD09_checkbox01list.append(True)
            UD09_checkbox02list.append(True)
            UD09_checkbox03list.append(True)
            UD09_checkbox04list.append(True)
            UD09_checkbox05list.append(True)
            
    UD10_dflist = [UD10_companylist,UD10_key1list,UD10_key2list,UD10_key3list,UD10_key4list,UD10_key5list,UD10_character01list,UD10_checkbox01list]
    UD10_df_unt = pd.DataFrame(UD10_dflist)
    UD10_df = UD10_df_unt.transpose()
    UD10_df.columns = ['Company', 'Key1','Key2','Key3','Key4','Key5','Character01','Checkbox01']
    
    UD09_dflist = [UD09_companylist,UD09_key1list,UD09_key2list,UD09_key3list,UD09_key4list,UD09_key5list,UD09_character01list,UD09_checkbox01list,UD09_checkbox02list,UD09_checkbox03list,UD09_checkbox04list,UD09_checkbox05list,]
    UD09_df_unt = pd.DataFrame(UD09_dflist)
    UD09_df = UD09_df_unt.transpose()
    UD09_df.columns = ['Company', 'Key1','Key2','Key3','Key4','Key5','Character01','Checkbox01','Checkbox02','Checkbox03','Checkbox04','Checkbox05']
    
    return UD10_df,UD09_df

# %%
def build_part(UD11_companylist,UD11_key1list,UD11_key2list,UD11_key3list,UD11_key4list,UD11_key5list):
    
    Part_Companylist = []
    Part_PartNumlist = []
    Part_Character05list = []
    Part_Character06list = []
    Part_Character08list = []
    Part_Checkbox11list = []
    Part_Character10list = []
    Part_Character11list = []
    Part_Character12list = []
    Part_Character13list = []
    
    # Build UI, Kinda
    
    print('Please enter the Variant Parent Part ID:')
    print('~~~~~~~~~~~~~~~~~~~~')
    VariantParent = input()
    print('~~~~~~~~~~~~~~~~~~~~')
    print('Thanks! Variant Parent Part ID Recorded.')
    print('~~~~~~~~~~~~~~~~~~~~')
    
    print('Please enter your desired Website (SA,SW,SA~SW):')
    print('~~~~~~~~~~~~~~~~~~~~')
    PDP_website = input()
    print('~~~~~~~~~~~~~~~~~~~~')
    print('Thanks! Desired Website Recorded.')
    print('~~~~~~~~~~~~~~~~~~~~')
    
    print('Do you need to create a new PDP? Enter Y/N:')
    print('~~~~~~~~~~~~~~~~~~~~')
    PDP_response = input()
    print('~~~~~~~~~~~~~~~~~~~~')
    print('Thanks! New PDP Request Recorded.')
    print('~~~~~~~~~~~~~~~~~~~~')
    
    if PDP_response == 'Y':
    
        Part_Companylist.append('SAINC')
        Part_PartNumlist.append(VariantParent)
        Part_Character05list.append(VariantParent)
        Part_Character06list.append(VariantParent + " COPY NEEDED")
        Part_Character08list.append(VariantParent + " COPY NEEDED")
        Part_Checkbox11list.append(True)
        Part_Character10list.append(UD11_key2list[0])
        Part_Character11list.append('')
        Part_Character12list.append('show')
        Part_Character13list.append(PDP_website)
    
    for index,company in enumerate(UD11_companylist):
    
        key1 = UD11_key1list[index]
        key2 = UD11_key2list[index]
        key3 = UD11_key3list[index]
        key4 = UD11_key4list[index]
        key5 = UD11_key5list[index]
        
        if key4 not in Part_PartNumlist:
        
            Part_Companylist.append(company)
            Part_PartNumlist.append(key4)
            Part_Character05list.append(key4)
            Part_Character06list.append('')
            Part_Character08list.append('')
            Part_Checkbox11list.append(True)
            Part_Character10list.append(key2)
            Part_Character11list.append(VariantParent)
            Part_Character12list.append('show')
            Part_Character13list.append(PDP_website)
            
    Part_dflist = [Part_Companylist,Part_PartNumlist,Part_Character05list,Part_Character06list,Part_Character08list,Part_Checkbox11list,Part_Character10list,Part_Character11list,Part_Character12list,Part_Character13list]
    Part_df_unt = pd.DataFrame(Part_dflist)
    Part_df = Part_df_unt.transpose()
    Part_df.columns = ['Company','PartNum','Character05','Character06','Character08','Checkbox11','Character10','Character11','Character12','Character13']
   
    return Part_df

# %%
def build_CSV(directory):
    
    filename,filepath = create_filepath(directory)
    
    UD11_df,UD11_companylist,UD11_key1list,UD11_key2list,UD11_key3list,UD11_key4list,UD11_key5list = build_UD11(filepath)
    
    output_filename = filename.replace('.xlsx','')
    foldername = output_filename + '_OUTPUT'
    folderpath = os.path.join(directory, foldername)
    
    os.makedirs(folderpath, exist_ok=True)
    
    if UD11_key1list[0] == 'Variant':
    
        UD10_df,UD09_df,UD08_df = build_variant(UD11_companylist,UD11_key1list,UD11_key2list,UD11_key3list,UD11_key4list,UD11_key5list)
        
        if 'DEL_' not in filename:
            
            print('Would you like to create a DMT-Part file? Enter Y/N:')
            print('~~~~~~~~~~~~~~~~~~~~')
            Part_Response = input()
            print('~~~~~~~~~~~~~~~~~~~~')
            print('Thanks! DMT-Part Response Recorded.')
            print('~~~~~~~~~~~~~~~~~~~~')
        
        else:
            Part_Response = 'N'
        
        if Part_Response == 'Y':
            Part_df = build_part(UD11_companylist,UD11_key1list,UD11_key2list,UD11_key3list,UD11_key4list,UD11_key5list) 
            Part_df_filepath = os.path.join(folderpath, filename + '_Part.csv')
            Part_df.to_csv(Part_df_filepath,index=False)
        else:
            Part_df_filepath = 'NONE'
            
        UD08_df_filepath = os.path.join(folderpath, filename + '_UD08.csv')
        UD09_df_filepath = os.path.join(folderpath, filename + '_UD09.csv')
        UD10_df_filepath = os.path.join(folderpath, filename + '_UD10.csv')
        UD11_df_filepath = os.path.join(folderpath, filename + '_UD11.csv')
        
        UD08_df.to_csv(UD08_df_filepath,index=False)
        UD09_df.to_csv(UD09_df_filepath,index=False)
        UD10_df.to_csv(UD10_df_filepath,index=False)
        UD11_df.to_csv(UD11_df_filepath,index=False)
        
        filepathlist = [Part_df_filepath,UD08_df_filepath,UD09_df_filepath,UD10_df_filepath,UD11_df_filepath]
        playlist_df_filepath = os.path.join(directory, filename + '_PLAYLIST.csv')
        
    if UD11_key1list[0] == 'Attribute':
    
        UD10_df,UD09_df = build_attribute(UD11_companylist,UD11_key1list,UD11_key2list,UD11_key3list)
        
        UD09_df_filepath = os.path.join(folderpath, filename + '_UD09.csv')
        UD10_df_filepath = os.path.join(folderpath, filename + '_UD10.csv')
        UD11_df_filepath = os.path.join(folderpath, filename + '_UD11.csv')
        
        UD09_df.to_csv(UD09_df_filepath,index=False)
        UD10_df.to_csv(UD10_df_filepath,index=False)
        UD11_df.to_csv(UD11_df_filepath,index=False)
        
        filepathlist = [UD09_df_filepath,UD10_df_filepath,UD11_df_filepath]
        playlist_df_filepath = os.path.join(directory, filename + '_PLAYLIST.csv')
        
    print('Done! Your DMT Files have been successfully generated.')
    print('~~~~~~~~~~~~~~~~~~~~')
    
    return filepathlist,playlist_df_filepath

# %%
def build_playlist(filepathlist,included_tables):
    
    tablelist = []
    new_filepathlist = []
    addlist = []
    updatelist = []
    deletelist = []
    waitlist = []
    
    for filepath in filepathlist:
        if filepath != 'NONE':
            
            table = filepath.split('_')[-1]
            table = table.replace('.csv','')
            
            if table in included_tables or 'Part' in table:
            
                if 'DEL_' in filepath:
                
                    tablelist.append(table)
                    new_filepathlist.append(filepath)
                    addlist.append(False)
                    updatelist.append(False)
                    deletelist.append(True)
                    waitlist.append(True)
            
                else:
                
                    tablelist.append(table)
                    new_filepathlist.append(filepath)
                    addlist.append(True)
                    updatelist.append(True)
                    deletelist.append(False)
                    waitlist.append(True)
            
    playlist_dflist = [tablelist,new_filepathlist,addlist,updatelist,deletelist,waitlist]
    playlist_df_unt = pd.DataFrame(playlist_dflist)
    playlist_df = playlist_df_unt.transpose()
    playlist_df.columns = ['Import','Source','Add','Update','Delete','Wait']
    
    return playlist_df

# %%
def build_final():
    
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('-------------------------------------------------------------------------------')
    print('Welcome Braden! I hope you get a dopamine hit from this increased productivity!')
    print('-------------------------------------------------------------------------------')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('Please enter the directory that your file(s) are located within:')
    
    directory = create_directory()
    
    print('~~~~~~~~~~~~~~~~~')
    print('Thanks! Directory Recorded')
    print('~~~~~~~~~~~~~~~~~')
    print('How would you like to build your playlist? Enter 1/2/3:')
    print('1: Delete Only')
    print('2: Add Only')
    print('3: Delete & Add')
    
    playlist_type = input()
    
    print('~~~~~~~~~~~~~~~~~')
    print('Thanks! Playlist Type Recorded')
    print('~~~~~~~~~~~~~~~~~')
    print('Please enter the tables to include in your playlist as a comma-delimited string (e.g. UD08,UD09,UD10,UD11):')
    
    included_tables = input()
    
    print('~~~~~~~~~~~~~~~~~')
    print('Thanks! Included Tables Recorded')
    print('~~~~~~~~~~~~~~~~~')
    
    if playlist_type != '3':
        
        filepathlist,playlist_df_filepath = build_CSV(directory)
        
        playlist_df = build_playlist(filepathlist,included_tables)
        playlist_df.to_csv(playlist_df_filepath,index=False)
    
    elif playlist_type == '3':
        
        print('XXXXXXXXXXXXXXXXXXXXXXXX')
        print('BUILDING DELETE FILES')
        print('XXXXXXXXXXXXXXXXXXXXXXXX')
        
        filepathlist_DEL,playlist_df_filepath = build_CSV(directory)
        
        print('++++++++++++++++++++++++')
        print('BUILDING ADD FILES')
        print('++++++++++++++++++++++++')
        
        filepathlist_ADD,playlist_df_filepath = build_CSV(directory)
        
        filepathlist = filepathlist_DEL + filepathlist_ADD
        
        playlist_df = build_playlist(filepathlist,included_tables)
        playlist_df.to_csv(playlist_df_filepath,index=False)
    
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('-------------------------------------------------------------------------------')
    print('Congrats! Your playlist has been created successfully. Enjoy the dopamine!')
    print('-------------------------------------------------------------------------------')
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('')
    print('   |   |   ')
    print('     ^     ')
    print(' |_______| ')

# %%
# Press Shift+Enter to Start

build_final()

# %%



