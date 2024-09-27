
#%% remove column from df
import pandas as pd
Tech = 'Hydro'
pp = 'WAPP'
path = 'Timeseries/'+Tech+'_'+pp+'.csv'
df = pd.read_csv(path)
# Drop all columns that contain 'EGY' in their column name
columns_to_drop = df.filter(like='NGA').columns
df.drop(columns=columns_to_drop, axis=1, inplace=True)
df.to_csv(path, index=False)


# %% fix date format
import pandas as pd
tech = 'Hydro'
path = 'Timeseries/'+ tech +'_NGA.csv'
df = pd.read_csv(path)
df['date'] = pd.to_datetime(df['date']).dt.strftime('%d/%m/%Y %H:%M')
df.to_csv(path, index=False)

# %%
tech ='Timeseries/Wind'
p_NAPP = tech+'_NAPP.csv'
p_EGY = tech+'_EGY.csv'

df_NAPP = pd.read_csv(p_NAPP)
df_EGY = pd.read_csv(p_EGY, usecols=lambda column: column != df_EGY.columns[0])
df_combined = pd.concat([df_NAPP, df_EGY], axis=1)

# Save the combined DataFrame to a new CSV file
df_combined.to_csv(p_NAPP, index=False)
# %%
