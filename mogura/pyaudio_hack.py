# based on pyaudio 0.2.13

import base64
import pyaudio
import locale

pa = pyaudio.pa

class PyAudioHack(pyaudio.PyAudio):

    def get_device_info_by_index_hack(self, device_index):
        """Returns the device parameters for device specified in `device_index`
        as a dictionary. The keys of the dictionary mirror the data fields of
        PortAudio's ``PaDeviceInfo`` structure.

        :param device_index: The device index
        :raises IOError: Invalid `device_index`.
        :rtype: dict
        """
        return self._make_device_info_dictionary_hack(
            device_index,
            pa.get_device_info(device_index))

    def _make_device_info_dictionary_hack(self, index, device_info):
        """Creates a dictionary like PortAudio's ``PaDeviceInfo`` structure.

        :rtype: dict
        """
        device_name = device_info.name

        # Attempt to decode device_name. If we fail to decode, return the raw
        # bytes and let the caller deal with the encoding.
        os_encoding = locale.getpreferredencoding(do_setlocale=False)
        for codec in [os_encoding, "utf-8"]:
            try:
                device_name = device_name.decode(codec)
                break
            except:
                pass

        device_name_bytes = device_info.name
        device_name_bytes_base64 = base64.b64encode(device_name_bytes).decode('utf-8')
        device_name_utf8 = device_name_bytes.decode('utf-8')

        return {'index': index,
                'structVersion': device_info.structVersion,
                'name': device_name,
                'hostApi': device_info.hostApi,
                'maxInputChannels': device_info.maxInputChannels,
                'maxOutputChannels': device_info.maxOutputChannels,
                'defaultLowInputLatency':
                device_info.defaultLowInputLatency,
                'defaultLowOutputLatency':
                device_info.defaultLowOutputLatency,
                'defaultHighInputLatency':
                device_info.defaultHighInputLatency,
                'defaultHighOutputLatency':
                device_info.defaultHighOutputLatency,
                'defaultSampleRate':
                device_info.defaultSampleRate,
                'name_bytes_base64':
                device_name_bytes_base64,
                'name_utf8':
                device_name_utf8}
