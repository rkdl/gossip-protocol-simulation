# -*- coding: utf-8 -*-
import random
from argparse import ArgumentParser, ArgumentTypeError


def is_positive_integer(supposed_positive):
    value = int(supposed_positive)
    if value <= 0:
        raise ArgumentTypeError('{0} is not an positive integer'.format(value))
    return value


def parse_cmd_args():
    cmd_parser = ArgumentParser()
    cmd_parser.add_argument('-n',
                            type=is_positive_integer,
                            dest='nodes_count',
                            default=20)
    cmd_parser.add_argument('-i',
                            type=is_positive_integer,
                            dest='repeats',
                            default=1000)
    cmd_parser.add_argument('--advanced-algo',
                            dest='advanced_algo',
                            action='store_true')
    return cmd_parser.parse_args()


class Gossiper:
    NODES_TO_MULTICAST = 4

    class Node:
        def __init__(self):
            self.received = False
            self.transmits = False

        def send_to(self, recipients):
            for recipient in recipients:
                if not recipient.received:
                    recipient.received = True
                    recipient.transmits = True
            self.transmits = False

    def __init__(self, nodes_count=20, gossip_runs=1000):
        self.nodes = [self.Node() for _ in range(nodes_count)]
        self.gossip_runs = gossip_runs
        self.total_success_rate = 0
        self.total_iterations = 0

    def _reset_nodes(self):
        for node in self.nodes:
            node.received = False
            node.transmits = False

    def reset(self):
        self._reset_nodes()
        self.total_iterations = 0

    def _multicast(self):
        stage_first_transmission = True
        for node in self.nodes:
            if node.transmits:
                # Since we don't need to transmit the packet to the node itself
                nodes = [x for x in self.nodes if x is not node]
                recipients = random.sample(nodes, self.NODES_TO_MULTICAST)
                node.send_to(recipients)

                if stage_first_transmission:
                    self.total_iterations += 1
                    stage_first_transmission = False

                self._multicast()

    def _spread_gossip(self):
        def initialize_first_transmitter():
            first_transmitter = random.choice(self.nodes)
            first_transmitter.received = True
            first_transmitter.transmits = True

        self._reset_nodes()
        initialize_first_transmitter()
        self._multicast()

        success_status = all(n.received for n in self.nodes)
        return success_status

    def run(self):
        successful_count = 0
        for _ in range(self.gossip_runs):
            success = self._spread_gossip()
            if success:
                successful_count += 1
        self.total_success_rate = successful_count / self.gossip_runs


class GossiperAdvanced(Gossiper):
    def __init__(self, nodes_count=20, gossip_runs=1000):
        super().__init__(nodes_count, gossip_runs)

    def _multicast(self, src=None):
        stage_first_transmission = True
        for node in self.nodes:
            if node.transmits:
                # Since we don't need to transmit the packet to the node itself
                # and to the source node
                nodes = [n for n in self.nodes if
                         n is not node and n is not src]
                recipients = random.sample(nodes, self.NODES_TO_MULTICAST)
                node.send_to(recipients)

                if stage_first_transmission:
                    self.total_iterations += 1
                    stage_first_transmission = False

                self._multicast(node)


def main():
    args = parse_cmd_args()
    if not args.advanced_algo:
        simulator = Gossiper(args.nodes_count, args.repeats)
    else:
        simulator = GossiperAdvanced(args.nodes_count, args.repeats)

    simulator.run()
    percentage = simulator.total_success_rate * 100
    print('In {}% cases all nodes received the packet'.format(percentage))
    print('Total iterations count: {}'.format(simulator.total_iterations))


if __name__ == '__main__':
    main()
