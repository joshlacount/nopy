import argparse
import asyncio
import os
import sys
import typing

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f"{SCRIPT_DIR}/src")

import nopy


def parse_args(
    args: typing.Optional[list[str]] = None,
    namespace: typing.Optional[argparse.Namespace] = None
) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--login", help="Use phone number to login and get tokens")

    return parser.parse_args(args=args, namespace=namespace)

async def main():
    args = parse_args()

    if args.login is not None:
        client = nopy.NoplaceClient(args.login)
        try:
            request_id = await client.send_otp()
            otp = input("enter otp: ")
            access_token = await client.verify_otp(request_id, otp)
            id_token, refresh_token, expires_in = await client.sign_in(access_token)
            print(f"ID Token: {id_token}\nRefresh Token: {refresh_token}\nExpires In: {expires_in}")
        except nopy.NoplaceClientException as e:
            print(e.msg)
            print(await e.resp.text())


if __name__ == "__main__":
    asyncio.run(main())

