
DEFAULT_SMOOTH_ITERATIONS = 15

def sphericity_wadell(volume, surface_area):
    # "Hakon Wadell defined sphericity as the surface area of a sphere of the same volume as the particle divided by the actual surface area of the particle."
    # https://en.wikipedia.org/wiki/Sphericity
    # https://www.journals.uchicago.edu/doi/10.1086/624298
    import math
    return pow(math.pi, 1/3) * pow(6 * volume, 2/3) / surface_area

def sphericity_legland(volume, surface_area):
    # https://imagej.net/plugins/morpholibj#shape-factors
    import math
    return 36 * math.pi * pow(volume, 2) / pow(surface_area, 3)

def solidity(surface_volume, convex_hull_volume):
    return surface_volume / convex_hull_volume

def surface_meshes(label_image, smooth_iterations:int=DEFAULT_SMOOTH_ITERATIONS):
    import numpy as np
    import vedo

    result = {}
    for label in np.unique(label_image):
        if label == 0: # skip background
            continue
        
        binary_image = np.asarray((label_image == label) * 1)
        
        extended_binary_image = np.zeros([s + 2 for s in binary_image.shape])
        extended_binary_image[1:-1,1:-1,1:-1] = binary_image
        
        volume = vedo.Volume(extended_binary_image)
        surface = volume.isosurface(threshold=0.5)

        surface = surface.clean()

        # might work but takes very long time:
        # surface = surface.smooth_mls_2d()
        # might work but takes long time:
        if smooth_iterations > 0:
            surface = surface.smooth(niter=smooth_iterations)

        result[label] = surface
    
    return result

def measure(label_image, smooth_iterations:int=DEFAULT_SMOOTH_ITERATIONS):
    import numpy as np
    import pandas as pd
    import math
    import vedo
    
    result = {
        "label":[],
        "surface_area":[],
        "volume":[],
        "convex_hull_area":[],
        "convex_hull_volume":[],
        "solidity":[],
        "sphericity_wadell":[],
        "sphericity_legland":[],
    }
    
    for label, surface in surface_meshes(label_image, smooth_iterations=smooth_iterations).items():
        
        convex_hull = vedo.shapes.ConvexHull(surface)

        surface_area = surface.area()
        surface_volume = surface.volume()
        
        convex_hull_area = convex_hull.area()
        convex_hull_volume = convex_hull.volume()
        
        result["label"].append(label)
        result["surface_area"].append(surface_area)
        result["volume"].append(surface_volume)
        result["convex_hull_area"].append(convex_hull_area)
        result["convex_hull_volume"].append(convex_hull_volume)
        result["solidity"].append(solidity(surface_volume, convex_hull_volume))
        result["sphericity_wadell"].append(sphericity_wadell(surface_volume, surface_area))
        result["sphericity_legland"].append(sphericity_legland(surface_volume, surface_area))

    return pd.DataFrame(result)
