from . import FirmwareBase
from intelhex import IntelHex
import can
from canfix.globals import TWOWAY_CONN_CHANS
import struct
import time


class STM32Firmware(FirmwareBase):

  def __init__(self, filename, node, vcode, conn):
    super().__init__(filename, node, vcode, conn)
    self._ih = IntelHex(filename)

  def update_fw(self):
    self.start_download()  # This will set self.channel
    #for start_addr, stop_addr in self._ih.segments():
    self._ih[0x8008000] = 0x01
    self._ih[0x8008001] = 0x02
    self._ih[0x8008002] = 0x03
    self._ih[0x8008003] = 0x04
    self._ih[0x8008004] = 0x05
    self._ih[0x8008005] = 0x06
    self._ih[0x8008006] = 0x10

    self._ih[0x8008010] = 0x07
    self._ih[0x8008011] = 0x08
    self._ih[0x8008012] = 0x09
    self._ih[0x8008013] = 0x0a
    self._ih[0x8008014] = 0x0b
    self._ih[0x8008015] = 0x0c
    self._ih[0x8008016] = 0x0d
    self._ih[0x8008017] = 0x0e
    self._ih[0x8008018] = 0x11
    for start_addr, stop_addr in [(0x8008000, 0x8008006), (0x8008010, 0x8008018)]:
      msg = can.Message(arbitration_id=TWOWAY_CONN_CHANS + self.channel*2, is_extended_id =False,
                                data=struct.pack('II', start_addr, stop_addr - start_addr))
      self.can.send(msg)
      t0 = time.time()
      while True:
        rframe = self.can.recv()
        if (rframe.arbitration_id == TWOWAY_CONN_CHANS + self.channel*2 + 1):
          print("response to set_addr", rframe)
          break
        if (time.time() - t0) > .5:
          raise IOError("Timeout waiting for response to set_addr frame")

      # Send data
      for n in range(start_addr, stop_addr, 8):
        self.can.send(can.Message(arbitration_id=TWOWAY_CONN_CHANS + self.channel*2,  is_extended_id =False,
                                data=bytearray([self._ih[xx] for xx in range(n,n+8)])))
        t0 = time.time()
        while True:
          rframe = self.can.recv()
          if (rframe.arbitration_id == TWOWAY_CONN_CHANS + self.channel*2 + 1):
            #print("response to update_flash", rframe)
            break
          if (time.time() - t0) > .5:
            raise IOError("Timeout waiting for response to update_flash frame")

    # Send add 0, 0 to state we're done.
    self.can.send(can.Message(arbitration_id=TWOWAY_CONN_CHANS + self.channel*2,  is_extended_id =False,
                                data=struct.pack('II', 0, 0)))
    t0 = time.time()
    while True:
      rframe = self.can.recv()
      if (rframe.arbitration_id == TWOWAY_CONN_CHANS + self.channel*2 + 1):
        print("response to set_addr", rframe)
        break
      if (time.time() - t0) > .5:
        raise IOError("Timeout waiting for response to set_addr frame")
  

