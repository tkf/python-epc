from epc.client import EPCClient


def run_client(address, port):
    client = EPCClient((address, port))

    @client.register_function
    def pong(*args):
        print("PONG got {0}".format(args))
        return args
        # FIXME: calling echo here hangs!
        # return client.call_sync('echo', args, timeout=1)

    print("Server provides these methods:")
    print(client.methods_sync())

    print("Calling (echo 1)")
    print("Got: {0}".format(client.call_sync('echo', [1])))

    print("Calling (ping-pong 111 222 333)")
    print("Got: {0}".format(client.call_sync('ping-pong', [111, 222, 333])))

    print("Closing client...")
    client.close()
    print("Closing client... Done!")


def main(args=None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        '--address', default='localhost')
    parser.add_argument(
        '--port', default=9999, type=int)
    ns = parser.parse_args(args)
    run_client(**vars(ns))


if __name__ == '__main__':
    main()
