import xarray as xr
import matplotlib.pyplot as plt
import geopandas as gpd
def xr_rasterize(gdf,
                 da,
                 attribute_col=False,
                 crs='epsg:3577',
                 transform=None,
                 name=None,
                 x_dim='lat',
                 y_dim='lon',
                 export_tiff= None,
                 **rasterio_kwargs):    
    """
    Rasterizes a geopandas.GeoDataFrame into an xarray.DataArray.
    
    Parameters
    ----------
    gdf : geopandas.GeoDataFrame
        A geopandas.GeoDataFrame object containing the vector/shapefile
        data you want to rasterise.
    da : xarray.DataArray
        The shape, coordinates, dimensions, and transform of this object 
        are used to build the rasterized shapefile. It effectively 
        provides a template. The attributes of this object are also 
        appended to the output xarray.DataArray.
    attribute_col : string, optional
        Name of the attribute column in the geodataframe that the pixels 
        in the raster will contain.  If set to False, output will be a 
        boolean array of 1's and 0's.
    crs : str, optional
        CRS metadata to add to the output xarray. e.g. 'epsg:3577'.
        The function will attempt get this info from the input 
        GeoDataFrame first.
    transform : affine.Affine object, optional
        An affine.Affine object (e.g. `from affine import Affine; 
        Affine(30.0, 0.0, 548040.0, 0.0, -30.0, "6886890.0) giving the 
        affine transformation used to convert raster coordinates 
        (e.g. [0, 0]) to geographic coordinates. If none is provided, 
        the function will attempt to obtain an affine transformation 
        from the xarray object (e.g. either at `da.transform` or
        `da.geobox.transform`).
    x_dim : str, optional
        An optional string allowing you to override the xarray dimension 
        used for x coordinates. Defaults to 'x'.    
    y_dim : str, optional
        An optional string allowing you to override the xarray dimension 
        used for y coordinates. Defaults to 'y'.
    export_tiff: str, optional
        If a filepath is provided (e.g 'output/output.tif'), will export a
        geotiff file. A named array is required for this operation, if one
        is not supplied by the user a default name, 'data', is used
    **rasterio_kwargs : 
        A set of keyword arguments to rasterio.features.rasterize
        Can include: 'all_touched', 'merge_alg', 'dtype'.
    
    Returns
    -------
    xarr : xarray.DataArray
    
    """
    
    # Check for a crs object
    try:
        crs = da.crs
    except:
        if crs is None:
            raise Exception("Please add a `crs` attribute to the "
                            "xarray.DataArray, or provide a CRS using the "
                            "function's `crs` parameter (e.g. 'EPSG:3577')")
    

    # Check if transform is provided as a xarray.DataArray method.
    # If not, require supplied Affine
    if transform is None:
        try:
            # First, try to take transform info from geobox
            transform = da.geobox.transform
        # If no geobox
        except:
            try:
                # Try getting transform from 'transform' attribute
                transform = da.transform
            except:
                # If neither of those options work, raise an exception telling the 
                # user to provide a transform
                raise Exception("Please provide an Affine transform object using the "
                        "`transform` parameter (e.g. `from affine import "
                        "Affine; Affine(30.0, 0.0, 548040.0, 0.0, -30.0, "
                        "6886890.0)`")
    
    # Get the dims, coords, and output shape from da
    da = da.squeeze()
    y, x = da.shape
    dims = list(da.dims)
    xy_coords = [da[y_dim], da[x_dim]]   
    
    # Reproject shapefile to match CRS of raster
    print(f'Rasterizing to match xarray.DataArray dimensions ({y}, {x}) '
          f'and projection system/CRS (e.g. {crs})')
    
    try:
        gdf_reproj = gdf.to_crs(crs=crs)
    except:
        #sometimes the crs can be a datacube utils CRS object
        #so convert to string before reprojecting
        gdf_reproj = gdf.to_crs(crs={'init':str(crs)})
    
    # If an attribute column is specified, rasterise using vector 
    # attribute values. Otherwise, rasterise into a boolean array
    if attribute_col:
        
        # Use the geometry and attributes from `gdf` to create an iterable
        shapes = zip(gdf_reproj.geometry, gdf_reproj[attribute_col])

        # Convert polygons into a numpy array using attribute values
        arr = rasterio.features.rasterize(shapes=shapes,
                                          out_shape=(y, x),
                                          transform=transform,
                                          **rasterio_kwargs)

##########Read the dataset using xarray##########################
filename=r"D:\Desktop\NCEP_Reanalysis2_data\2m_Temp\air.2m.gauss.1980.nc"
da=xr.open_dataset(filename)
print(da)

############Read the individual variables in the dataset########
air=da.air
lat=da.lat
lon=da.lon
print(lon)
gdf = gpd.read_file("D:\Desktop\india updated state boundary.shp")

################ Subsetting in all dimensions###################
da1=da.sel(time='1980-02-02',lat=slice(40.5,7.5),lon=slice(68.0,90.5))
print(da1)
print(da1.air)

plot=da1.air.plot()
mask = xr_rasterize(gdf, da1)
masked_da = da1.where(mask)
plt.savefig("testcase3.png")

