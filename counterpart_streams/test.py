import Counterpart_streams as CS
dem = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/gebco_ep.tif"
rivers = 'C:/Users/vital/Documents/Rivers.shp'
field = 'ID'
dist = 5000
acc_mask_filter = 40
counterpart_vectors = "C:/Users/vital/Desktop/Kursovaya/DEMGEN/_Export/counterpart_vectors.shp"


CS.counterpart_streams(dem, rivers, field, dist, acc_mask_filter, counterpart_vectors)