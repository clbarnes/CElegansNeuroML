from NeuroMLUtilities import ConnectionInfo
import PyOpenWorm as P

import logging

############################################################

#   A simple script to read the values in PyOpenWorm
#   Originally written by Mark Watts (github.com/mwatts15)

############################################################

logger = logging.getLogger("OpenWormReader")

class OpenWormReader:
    def __init__(self):
        logger.info("Initialising OpenWormReader")
        P.connect()
        self.net = P.Worm().get_neuron_network()
        self.all_connections = self.net.synapses()
        logger.info("Finished initialising OpenWormReader")

    def read(self):
        conns = []
        cells = []
        for s in self.all_connections:
            pre = str(s.pre_cell())
            post = str(s.post_cell())
            syntype = str(s.syntype())
            num = int(s.number())
            synclass = str(s.synclass())

            conns.append(ConnectionInfo(pre, post, num, syntype, synclass))

            if pre not in cells:
                cells.append(pre)
            if post not in cells:
                cells.append(post)

        logger.info("Total cells read " + str(len(cells)))
        logger.info("Total connections read " + str(len(conns)))
        P.disconnect()
        return cells, conns

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(name)s - %(levelname)s: %(message)s')
    owr = OpenWormReader()
    owr.read()