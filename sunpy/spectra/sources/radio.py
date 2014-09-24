import xml.sax
import radio
import pprint

import xml.sax.handler
import numpy as np
import matplotlib.pyplot as plt 

from sunpy.util.cond_dispatch import ConditionalDispatch
from sunpy.spectra.spectrogram import LinearTimeSpectrogram, REFERENCE, get_day
from sunpy.time import parse_time

__all__ = ['RadioSpectrogram']

class RadioSweep(xml.sax.handler.ContentHandler):
    def __init__(self):
      self.inStartDate = False
      self.inFrequencies = False
      self.inValues = False
      self.inAntennaGain = False
      self.mapping = {}
 
    def startElement(self, name, attributes):
        if name == "Sweep":
            self.date = ''
            self.freq = ''
            self.values = ''
            self.gain = ''
        elif name == "StartDate":
            self.inStartDate = True
        elif name == "Frequencies":
            self.inFrequencies = True
        elif name == "Values":
            self.inValues = True
        elif name == "AntennaGain":
            self.inAntennaGain = True
 
    def characters(self, data):
        if self.inStartDate:
            self.date += data
        elif self.inValues:
            self.values += data
        elif self.inFrequencies:
            self.freq += data
        elif self.inAntennaGain:
            self.gain += data

    def endElement(self, name):
        array_made = lambda text: [float(x) for x in text.split(';')[:-1]]
        if name == "StartDate":
            self.inStartDate = False
            self.mapping[self.date] = {}
        if name == "Frequencies":
            self.inFrequencies = False
            self.mapping[self.date]['freq'] =  array_made(self.freq)
        elif name == "Values":
            self.inValues = False
            self.mapping[self.date]['values'] = array_made(self.values)
        elif name == "AntennaGain":
            self.inAntennaGain = False
            self.mapping[self.date]['gain'] = array_made(self.gain)


class RadioSpectrogram(LinearTimeSpectrogram):
    _create = ConditionalDispatch.from_existing(LinearTimeSpectrogram._create)
    create = classmethod(_create.wrapper())
    COPY_PROPERTIES = LinearTimeSpectrogram.COPY_PROPERTIES + [
        ('bg', REFERENCE)
    ]
   
    @classmethod
    def read(cls, filename, **kwargs):
        parser = xml.sax.make_parser()
        handler = RadioSweep()
        parser.setContentHandler(handler)
        parser.parse(filename)
        data_dict = handler.mapping
        slices = data_dict.keys()
        slices.sort()
        t0 = parse_time(slices[0])
        time_axis = [(parse_time(t)-t0).seconds for t in slices]
        freq_axis = np.array(data_dict[slices[0]]['freq'])
        data = np.column_stack((data_dict[l]['values'] for l in slices))
        
        t_label = 'Time [UT]'
        f_label = 'Frequency [??]' #This needs to be taken from xml
        content = ''

        t_init = t0
        start = t0
        end = len(data)
        t_delt = 60 # This need to be done automatically
        bg = data_dict[slices[0]]['values']

        return cls(data, time_axis, freq_axis, start, end, t_init, t_delt,
            t_label, f_label, content, bg)


    def __init__(self, data, time_axis, freq_axis, start, end,
            t_init, t_delt, t_label, f_label, content, bg):
        # Because of how object creation works, there is no avoiding
        # unused arguments in this case.
        # pylint: disable=W0613

        super(RadioSpectrogram, self).__init__(
            data, time_axis, freq_axis, start, end,
            t_init, t_delt, t_label, f_label,
            content, set(["RADIO"])
        )
        self.bg = bg

if __name__ == "__main__":
    opn = RadioSpectrogram.read("/tmp/barrido_example.xml")
    fig = plt.figure()
    opn.plot(vmin=-100, vmax=-50, linear=False)
    fig.show()
    print "Press return to exit"
    raw_input()
