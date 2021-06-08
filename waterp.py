# waterp returns true if passed lat and lon are in water.

import sys, getopt
import shapefile

def axis_crossings(x, poly):
    # point . a 2-tuple x,y
    # poly . an array of 2-tuples vertices
    # this poly array has a transform (shift to origin) done
    # and will become polygon array
    # returns the winding number w
    # w=0 means x is not inside polygon
    # w>0 means polygon winds around x n times counter clockwise
    # w<0 means polygon winds around x (-n) times counterclockwise

    polygon = []
    
    # we translate the point to be tested to (0,0)
    # we iterate over all vertices v and translate them too
    for v in poly:
        polygon.append((v[0]-x[0], v[1]-x[1]))

    w = 0 # winding number

    # for each segment of the polygon:
    # determine whether that segment crosses the positive x-axis + direction
    # if crossing from below: w+=1
    # if crossing from above: w-=1

    n = len(polygon)
    
    for i in range(n):
        #print(i)
        # determine which vertex to visit next
        i1 = i+1
        if i == n-1: i1 = 0
        
        if polygon[i][1]*polygon[i1][1]<0:
            # only +*- multiplication yields a negative product.
            # edge crosses x axis
            f = lambda p1, p2 :  p1[0] + p1[1]*(p2[0]-p1[0]) / p1[1]-p2[1]
            r = f(polygon[i],polygon[i1])
            # r is x coord of intersection
            
            if r > 0: # crosses positive x-axis
                if polygon[i][1] < 0:
                    w+=1
                else:
                    w-=1
        elif polygon[i][1] == 0 and polygon[i][0] > 0:
            # v_i is on the positive x axis
            if polygon[i1][1] > 0:
                w+=0.5
            else:
                w-=0.5
        elif polygon[i1][1] == 0 and polygon[i1][0] > 0:
            # v_i+1 is on positive x axis
            if polygon[i][1] < 0:
                w+=0.5
            else:
                w-=0.5
    return w


def point_in_polygon(x, polygon):
    # x is a tuple with the position of the point
    # polygon is an array of tuples each is a vertex
    is_inside = None
    # +w is clockwise winding of polygon around x
    w = axis_crossings(x, polygon)
    if w != 0:
        is_inside = True
    else:
        is_inside = False
    return is_inside

def bbox(polygon):
    # return a polygon (square) of the bounding box for the passed polygon
    # which is an array of tuples
    lowest_x = polygon[0][0]
    highest_x = polygon[0][0]
    lowest_y = polygon[0][1]
    highest_y = polygon[0][1]

    # check every vertex to see if higher or lower than current max and min
    for vertex in polygon:
        #print(vertex)
        if vertex[0] < lowest_x:
            lowest_x = vertex[0]
        elif vertex[0] > highest_x:
            highest_x = vertex[0]
        if vertex[1] < lowest_y:
            lowest_y = vertex[1]
        elif vertex[1] > highest_y:
            highest_y = vertex[1]

    # now we have our bounding coordinates
    # return a square polygon
    return [(lowest_x,lowest_y),
            (lowest_x,highest_y),
            (highest_x,highest_y),
            (highest_x,lowest_y)]


def main(argv):
    lat = None
    lon = None

    try:
        opts, args = getopt.getopt(argv,"ht:n:",["lat=","lon="])
    except getopt.GetoptError:
        print("waterp.py -t <latitude> -n <longitude>")
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("waterp. Returns True if coordinate is water\nUsage: waterp.py -t <latitude> -n <longitude>")
        elif opt in ("-t","--lat"):
            lat = float(arg)
        elif opt in ("-n","--lon"):
            lon = float(arg)

    print("Lat: ",lat)
    print("Lon: ",lon)

    # using x,y coordinates.
    # Google Earth and other places will commonly use y,x or lat,lon
    # Be careful.
    x = (lon,lat)

    # load in landmass shapefile
    try:
        # loading .shx file may improve read speeds.
        land_110m_shp, land_110m_dbf = open("ne_110m_land.shp","rb"), \
            open("ne_110m_land.dbf","rb")
        print("Landmass shape file and dbf loaded!")
    except:
        print("Missing ne_110m_land.shp or ne_110m_land.dbf files")
        sys.exit(2)

    # load the shapefile using pyshp
    sf = shapefile.Reader(shp=land_110m_shp, dbf=land_110m_dbf)
    # print(sf.shapeType) # == 5, polygon. Will not work otherwise.
    shapes = sf.shapes()
    # print(len(shapes)) # 127 <- how many polygons we need to iterate through
    
    for shape in shapes:
        # vertices is [(x,y),...,(xn,yn)]
        vertices = shape.points
        # square box which fits shape
        # also a list of tuples for each vertex
        bounding_square = bbox(vertices)

        if point_in_polygon(x, bounding_square): # inside bounding box
            if point_in_polygon(x, vertices):
                print(x, " is not on water")
                return False
            else:
                print(x, " is on water")
                return True # not inside the land polygon. in water.
        else:
            # not inside bounding box of particular shape
            # 173 shapes with many sides each is a lot of iteration
            # o: so is making bounding boxes?
            # not in bounding box means not applicable
            pass

    # if we end up here we have gone through all shapes and none are applicable
    # if the coordinates were not on any land polygons, they are in the water.
    print(x, "was not on any bounding boxes, must be in water")
    return False

    
if __name__ == "__main__":
    main(sys.argv[1:]) # argv[0] is name of program.





