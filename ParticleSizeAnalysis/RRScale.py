import numpy as np
from numpy import ma
import matplotlib.ticker as mticker
from matplotlib import scale as mscale
from matplotlib import transforms as mtransforms
from matplotlib.ticker import FixedLocator, FuncFormatter

class WeibullScale(mscale.ScaleBase):
    """
    Scales data in range 1 to 99.9 using the below function:

    The scale function:
      y' = log10(log10(100/y))

    The inverse scale function:
      y = 100/(10**(10**y'))
    """
    name = "rry"
    
    def __init__(self, axis, *, thresh=0.01, **kwargs):
        """
        Any keyword arguments passed to ``set_xscale`` and ``set_yscale`` will
        be passed along to the scale's constructor.

        thresh: The degree above which to crop the data.
        """
        super().__init__(axis)
        if thresh < 0.01:
            raise ValueError("thresh must be less than 99.9")
        self.thresh = thresh
        
    def get_transform(self):
        return self.RRTransform(self.thresh)
        
    def set_default_locators_and_formatters(self, axis):
        """
        Override to set up the locators and formatters to use with the
        scale. This is only required if the scale requires custom 
        locaters and formatters.
        
        In our case, the Weibull uses a fixed locator from 0.01 to 99.9
        
        """
        scaleValues = np.array([0.01, 0.1, 1, 5, 10, 20, 30, 40, 50, 60, 
                                    70, 80, 90, 95, 99])
        fmt = mticker.ScalarFormatter()
        
        axis.set(major_locator=FixedLocator(scaleValues), major_formatter=fmt,
                 minor_formatter=fmt)
        
    def limit_range_for_scale(self, vmin, vmax, minpos):
        """
        
        Override to limit the bounds of the axis to the domain of the
        transform.  In the case of RR, the bounds should be
        limited to the threshold that was passed in.  Unlike the
        autoscaling provided by the tick locators, this range limiting
        will always be adhered to, whether the axis range is set
        manually, determined automatically or changed through panning
        and zooming.
        
        """
        
        return max(vmin, self.thresh), min(vmax, 99.9)
    
    class RRTransform(mtransforms.Transform):
        # There are two value members that must be defined.
        # ``input_dims`` and ``output_dims`` specify number of input
        # dimensions and output dimensions to the transformation.
        # These are used by the transformation framework to do some
        # error checking and prevent incompatible transformations from
        # being connected together.  When defining transforms for a
        # scale, which are, by definition, separable and have only one
        # dimension, these members should always be set to 1.
        
        input_dims = output_dims = 1
        
        def __init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh
            
        def transform_non_affine(self, a):
            """
            This transform takes a numpy array and returns a transformed copy.
            Since the range of the Mercator scale is limited by the
            user-specified threshold, the input array must be masked to
            contain only valid values.  Matplotlib will handle masked arrays
            and remove the out-of-range data from the plot.  However, the
            returned array *must* have the same shape as the input array, since
            these values need to remain synchronized with values in the other
            dimension.
            """
            
            masked = ma.masked_where((a < self.thresh), a)
            if masked.mask.any():
                return mscale.np.log(ma.log(100*masked**-1))
            else:
                return mscale.np.log(mscale.np.log(100*a**-1))
            
        def inverted(self):
            """
            Override this method so Matplotlib knows how to get the
            inverse transform for this transform.
            """
        
            return WeibullScale.InvertedRRTransform(self.thresh)
           
    class InvertedRRTransform(mtransforms.Transform):
        input_dims = output_dims = 1
            
        def __init__(self, thresh):
            mtransforms.Transform.__init__(self)
            self.thresh = thresh
                
        def transform_non_affine(self, a):
            return 10**(2-(10**(a)))
        
        def inverted(self):
            return WeibullScale.RRTransform(self.thresh)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        