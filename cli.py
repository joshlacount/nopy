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
    parser.add_argument(
        "-l", "--login", help="Use phone number to login and get tokens", metavar="phone_number"
    )
    parser.add_argument(
        "-r", "--refresh-id-token", help="Use a refresh token to get a new ID token",
        metavar="refresh_token"
    )

    return parser.parse_args(args=args, namespace=namespace)

def print_tokens(id_token: str, refresh_token: str, expires_in: int) -> None:
    print(f"ID Token: {id_token}\nRefresh Token: {refresh_token}\nExpires In: {expires_in}")

async def main():
    args = parse_args()

    if args.login is not None:
        client = nopy.NoplaceClient(args.login)
        try:
            request_id = await client.send_otp()
            otp = input("enter otp: ")
            access_token = await client.verify_otp(request_id, otp)
            id_token, refresh_token, expires_in = await client.sign_in(access_token)
            print_tokens(id_token, refresh_token, expires_in)
        except nopy.NoplaceClientException as e:
            print(e.msg)
            if e.resp is not None:
                print(await e.resp.text())
    if args.refresh_id_token is not None:
        client = nopy.NoplaceClient(refresh_token=args.refresh_id_token)
        try:
            id_token, refresh_token, expires_in = await client.refresh_id_token()
            print_tokens(id_token, refresh_token, expires_in)
        except nopy.NoplaceClientException as e:
            print(e.msg)
            if e.resp is not None:
                print(await e.resp.text())
            


if __name__ == "__main__":
    asyncio.run(main())

