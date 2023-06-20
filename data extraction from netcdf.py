
import xarray as xr

filename=r"D:\Desktop\NCEP_Reanalysis2_data\2m_Temp\air.2m.gauss.1980.nc"
da=xr.open_dataset(filename)
print(da)

air=da.air
lat=da.lat
lon=da.lon
print(lon)
print(air)