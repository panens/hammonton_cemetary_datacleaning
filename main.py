import pandas as pd 
import numpy as np
import re
import matplotlib.pyplot as plt 


df_a= pd.read_csv("old_graveyard_data/Data/halloween2019a.csv") #reading in file 2019a to df_a
df_b= pd.read_csv("old_graveyard_data/Data/halloween2019b.csv") #reading in file 2019b to df_b
df_c= pd.read_csv("old_graveyard_data/Data/halloween2019c.csv") #reading in file 2019c to df_c
df_n= pd.read_csv("new_graveyard_data/halloween2022.csv") #reading in file 2022 - the new file - to df_n

#in order to combine data into 1 file, we need to make sure that the data is formatted correctly, and reformat if it is not. 

print(df_a.head()) #Since we are interested in data separated by gender, this df is not useful to us at all. 

print("DF_B")
print(df_b.head()) #date of birth and date of death is in all sorts of formats. so is the gender column 
print(df_b.tail())

print("DF_N")
print(df_n.head()) #I collected only birth year and death year for all the records. I also did not separate first and last name when I collected data. 
print(df_n.tail())

#Since we don't need the first name or the last name for anything specific, we can simply use 1 column, column name, for the entire recorded name. 

df_b["Name"] = df_b["FirstName"] + df_b[" LastName"] 
#The code above was erroring out, the header seems to have a space before the name. 
print(df_b.head()) 
print(df_b[" DOB"])

"""
Used to check how many null lines there are
print("AMOUNT OF NULL") #check for null values 
print(df_b[" DOB"].isnull().sum()) #zero of them 
print(df_b[" DOD"].isnull().sum())
print(df_b[" DOD"].tail()) #5 of these 
"""
df_b = df_b.dropna() #drop the null values as we cannot calculate the lifespan from a null value. 
df_c = df_c.dropna() #drop the null values from this df as well. 
"""
I used these 4 to see if all males actually add up to 66 at the end and they did 
print(df_b[" Sex"].unique())
print(df_b[df_b[" Sex"] == ' m'].count())
print(df_b[df_b[" Sex"] == 'Male'].count())
print(df_b[df_b[" Sex"] == 'male'].count())
print(df_b[df_b[" Sex"] == 'M'].count())
"""


def get_only_year(column, dataframe): #function that gets only the 4 digit year from any date format. 
    #modified to take column and dataframe so I can use the same function for df_b, df_c, for both columns birth and death
    
    array = [] #empty array 
    for i in dataframe[column]: #for each element in df["column"]
        array.append(int(re.search("([0-9]{4})", i).group(1))) #finds a 4 digit in a string i and returns the 4 digits. 
    
    return array

def clean_sex(column, dataframe): 
    array = []
    for i in dataframe[column]: 
        if "f" in i.lower(): #f goes first because word female contains letter m" 
            array.append("f")
        elif "m" in i.lower(): #if it is not female, f, F... then check if it is male 
            array.append("m")
        else: #if neither return error
            array.append("JUST TESTING - THIS SHOULDNT EXIST")
            
    return array 


birth_year_array = get_only_year(" DOB", df_b) #gets the 4digit year array 
df_b["BirthYear"] = birth_year_array #places the array above to BirthYear Column 

death_year_array = get_only_year(" DOD", df_b) #gets the 4digit year array 
df_b["DeathYear"] = death_year_array #places the array above to DeathYear Column. 

clean_sex_array_b = clean_sex(" Sex", df_b)
df_b["CleanSex"] = clean_sex_array_b

"""
Just to check the count of all male in df_b
print("HERE")
print(df_b[df_b["CleanSex"] == 'm'].count())
"""

print(df_b.head()) #df_b is clean now. 

print("DF_C")
print(df_c.head()) #date of birth and date of death is in all sorts of formats. so is the gender column 
print(df_c.tail()) #same cleanup needed as for df_b

birth_array = get_only_year("DOB", df_c)
df_c["BirthYear"] = birth_array

death_array = get_only_year("DOD", df_c)
df_c["DeathYear"] = death_array 

clean_sex_array_c = clean_sex("Sex", df_c)
df_c["CleanSex"] = clean_sex_array_c

print(df_c.head()) #df_c is clean now. 

#df_n is collected by me and all rows are formatted the propper way. 

#now that the data is clean, we want to combine it to make calculations. 

df_1 = df_b[["Name", "BirthYear", "DeathYear", "CleanSex"]]
df_2 = df_c[["Name", "BirthYear", "DeathYear", "CleanSex"]]
df_3 = df_n[["name", "birth", "death", "gender "]]
df_3.columns = ["Name", "BirthYear", "DeathYear", "CleanSex"] # Changing df_n column headers to match the cleaned headers from db_b and db_c

df_combined = pd.concat([df_1,df_2,df_3]) #combines the 3 dataframes

df_combined["LifeSpan"] = df_combined["DeathYear"] - df_combined["BirthYear"] 

print(df_combined[df_combined["LifeSpan"] < 0]) #The lifespan cannot be negative, so these rows of data need to be handled differently

#It looks like 1058 is a typo. Since we do not know is the death year 1958 or is it 1858 and the birth and death are switched, we can omit this row. 

df_combined = df_combined[df_combined["LifeSpan"] > -200] #deletes rows where lifespan is less than or equal to -200

print(df_combined[df_combined["LifeSpan"] < 0]) 

#the remaining rows can be dealt with the same way as the one row above. However, it seems reasonable to conclude 
#that the column birth and death were swapped. I will handle this issue by considering what their lifespan would be
#if the data was entered correctly. Instead of swapping the birth and death year values for these rows, we can simply 
#calculate the absolute value of the difference. 

#since the 1 unlikely row was already removed, we can simply recall the following 

df_combined["LifeSpan"] = abs(df_combined["DeathYear"] - df_combined["BirthYear"])

#print(df_combined[df_combined["LifeSpan"] < 0]) #just checking if there are any negative results. 

stored = df_combined["LifeSpan"].describe() #we can describe the LifeSpan data

print(f'Median Life Expectancy is {stored["50%"]}')

male = df_combined[df_combined["CleanSex"] == "m"]
female = df_combined[df_combined["CleanSex"] == "f"]

stored_m = male["LifeSpan"].describe()
stored_f = female["LifeSpan"].describe()

print(f'Median Male Life Expectancy is {stored_m["50%"]}')
print(f'Median Female Life Expectancy is {stored_f["50%"]}')

#we can look if there are any outliers in our data 

df_combined.boxplot(by = "CleanSex", column = ["LifeSpan"]) 
plt.savefig('BoxplotByGender.png')

#we can notice from the boxplots above that there are sveral outliers in female data. 
#all are under the age of 20. 

#If we wanted to focus in on adult deaths only we can just add the lifespan >= 18 filter. 

df_combined[df_combined["LifeSpan"] >= 18].boxplot(by = "CleanSex", column = ["LifeSpan"]) 
plt.savefig('BoxplotByGenderAdultsOnly.png')

stored2 = df_combined[df_combined["LifeSpan"] >= 18]["LifeSpan"].describe() #we can describe the LifeSpan data

print(f'Median Life Expectancy, if adulthood is reached, is {stored2["50%"]}')

male2 = df_combined[(df_combined["CleanSex"] == "m") & (df_combined["LifeSpan"] >= 18)]
female2 = df_combined[(df_combined["CleanSex"] == "f") & (df_combined["LifeSpan"] >= 18)]

stored_m2 = male2["LifeSpan"].describe()
stored_f2 = female2["LifeSpan"].describe()

print(f'Median Male Life Expectancy, if adulthood is reached, is {stored_m2["50%"]}')
print(f'Median Female Life Expectancy, if adulthood is reached, is {stored_f2["50%"]}')

#Our median summary data did not change much after focusing in only on adults, so we can revert back to all data together, including the mentioned outliers. 

mean_lifespan_by_sex = df_combined.pivot_table( 
    values = 'LifeSpan', #Use LifeSpan Values
    index = 'BirthYear', #Group By the Birth Year
    columns= 'CleanSex', #Pivot Values by gender
    aggfunc = 'mean' #calculate the mean of LifeSpan values
)
print (mean_lifespan_by_sex) #just so i can make sure it looks right. 
#in order for this data to show up properly, we would need the proper year of birth for every entry. 
#during the data cleanup I saw that there were entries that seemed to have birth year and death year reversed. 
#even though they're ok to calculate for lifespan, they are not accurately represented in this table because 
#death year is shown instead of  birth year. 

#fixup

def actual_birth_year(): 
    array = []
    for index, row in df_combined.iterrows(): 
        array.append(min(row["BirthYear"], row["DeathYear"]))
        index = index + 1
    return array


act_year = actual_birth_year()
df_combined["ActualBirthYear"] = act_year
print(df_combined)

mean_lifespan_by_sex_clean = df_combined.pivot_table( 
    values = 'LifeSpan', #Use LifeSpan Values
    index = 'ActualBirthYear', #Group By the Birth Year
    columns= 'CleanSex', #Pivot Values by gender
    aggfunc = ['mean','count'] #calculate the mean of LifeSpan values
)
print (mean_lifespan_by_sex_clean)

#now the data makes sense. 
#The pivot table mean_lifespan_by_sex_clean returns: 
#a row for each birth year in our data file 
#computed female mean and male mean for that year, 
#computed female count and male count that are used to calculate that mean 
#for example, row 1 is year 1810, the mean for female is unknown, because there is no female data for 1810
#in the same row, male mean is 89, and there was only 1 male data point born in 1810. 
#count can be used to express how "strong" (weighted) the mean calculation is. 

#mean_lifespan_by_sex_clean.plot.scatter(x=mean_lifespan_by_sex_clean.index,y=)
