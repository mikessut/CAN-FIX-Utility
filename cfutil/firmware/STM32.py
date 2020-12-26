"""
STM32 device type is 0xB4

Example command line usage:
python3 cfutil.py --channel=can0 --firmware-file=ahrs-stm32f429.hex \
  --target-node=0x12 --device-type=0xb4 --device-model=0x01 \
  --device-version=0x01 --node=1 -i

target-node identifies the node id of AHRS
device-type identifies STM32
device-model
device-version
node
"""

from . import FirmwareBase
from intelhex import IntelHex
import can
from canfix.globals import TWOWAY_CONN_CHANS
import struct
import time
import tqdm


SECTORS = {
    5: (0x8020000, 0x8040000),
    6: (0x8040000, 0x8060000),
    7: (0x8060000, 0x8080000),
    8: (0x8080000, 0x80A0000),
    9: (0x80A0000, 0x80C0000),
    10: (0x80C0000, 0x80E0000),
    11: (0x80E0000, 0x8100000),
}


class Driver(FirmwareBase):
    def __init__(self, filename, node, vcode, conn):
        super().__init__(filename, node, vcode, conn)
        self._ih = IntelHex(filename)

    def __send_recv(self, data, expected_ret):
        msg = can.Message(
            arbitration_id=TWOWAY_CONN_CHANS + self.channel * 2,
            is_extended_id=False,
            data=data,
        )
        self.can.send(msg)
        t0 = time.time()
        while True:
            rframe = self.can.recv()
            if rframe.arbitration_id == TWOWAY_CONN_CHANS + self.channel * 2 + 1:
                # print("response to set_addr", rframe)
                if rframe.data[0] != expected_ret:
                    raise IOError(
                        f"Expected {expected_ret} but received {rframe.data[0]}"
                    )
                break
            if (time.time() - t0) > 1:
                raise IOError("Timeout waiting for response")

    def __sectors_used(self):
        for sect, bnds in SECTORS.items():
            s = set(range(bnds[0], bnds[1])).intersection(
                set(range(self._ih.minaddr(), self._ih.maxaddr()))
            )
            if len(s) > 0:
                yield sect

    def download(self):
        self.start_download()  # This will set self.channel

        # Erase necessary sectors
        for sect in self.__sectors_used():
            self.__send_recv([sect], 0x1)

        # send code specifying done with erasing
        self.__send_recv([0xFF], 0x2)

        for ns, (start_addr, stop_addr) in enumerate(self._ih.segments()):
            print(f"Segment {ns+1} of {len(self._ih.segments())}")
            self.__send_recv(struct.pack("II", start_addr, stop_addr - start_addr), 0x3)

            # Send data
            for n in tqdm.tqdm(list(range(start_addr, stop_addr - 8, 8))):
                self.__send_recv(
                    bytearray([self._ih[xx] for xx in range(n, n + 8)]), 0x4
                )
            # last msg has a different return code
            self.__send_recv(bytearray([self._ih[xx] for xx in range(n, n + 8)]), 0x5)

        # Send addr 0, 0 to state we're done.
        self.__send_recv(struct.pack("II", 0, 0), 0x6)
