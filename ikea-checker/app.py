from argparse import ArgumentParser

import ikea_api
import asyncio

constants = ikea_api.Constants(country="fr", language="fr")
token = ikea_api.run(ikea_api.Auth(constants).get_guest_token())

async def get_deliveries(product, zip_code):
    services = await ikea_api.get_delivery_services(
        constants=constants,
        token=token,
        items={
            product: 1
        },
        zip_code=zip_code)
    return services.delivery_options

def ikea(args):
    deliveries = asyncio.run(get_deliveries(args.product, args.zip_code))
    for delivery in deliveries:
        print(f'{delivery.type} -> {delivery.service_provider} ({delivery.date})')
    exit(1) if not len(deliveries) else print('🎊')


parser = ArgumentParser(prog='ikea-checker')
parser.add_argument('-p', '--product', help='product you want to check availability', required=True)
parser.add_argument('-z', '--zip-code', help='zip-code used by the home check', required=True)
parser.set_defaults(func=ikea)

def main(args):
    '''ikea-checker allows you to check product availability'''
    args.func(args)


if __name__ == '__main__':
    main(parser.parse_args())