import os
import json
from operator import itemgetter
from itertools import groupby
import datetime

# Change working directory to the directory of the script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

f = open("./device_clients.json")

device_clients = json.load(f)

f.close()

f = open("./keep_clients.json")

keep_clients = json.load(f)

f.close()


def export(file_name: str, data: any) -> None:
    with open(file_name, mode="w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def traverse_device(child_dict, device_id):
    if device_id not in child_dict:
        return device_id
    else:
        for child in child_dict[device_id]:
            return traverse_device(child_dict, child)
        return device_id


# find_last_device before tuned
def find_last_device(client_belong_devices: []) -> str | None:
    all_client_macs = set()
    site_device_macs: dict[str, list[str]] = {}

    for tmp_client in client_belong_devices:
        all_client_macs.update(tmp_client["client_macs"])
        site_device_macs[tmp_client["device_id"]] = tmp_client["mac_pool"]

    child_dict: dict[str, list[str]] = {}
    root = client_belong_devices[0]
    for client in client_belong_devices:
        if not set(client["mac_pool"]).intersection(all_client_macs):
            root = client

        child_device_ids: set[str] = set()
        for device_id, device_mac_pool in site_device_macs.items():
            if (
                set(client["client_macs"]).intersection(set(device_mac_pool))
                and device_id != client["device_id"]
            ):
                if device_id in child_dict:
                    return None
                child_device_ids.add(device_id)

        if child_device_ids:
            child_dict.setdefault(client["device_id"], []).extend(child_device_ids)

    return traverse_device(child_dict, root["device_id"])


# new one
def find_last_device_1(client_belong_devices: []) -> str | None:
    all_client_macs = set()
    site_device_macs: dict[str, list[str]] = {}
    device_client_macs_set: dict[str, set[str]] = {}

    for tmp_client in client_belong_devices:
        all_client_macs.update(tmp_client["client_macs"])
        site_device_macs[tmp_client["device_id"]] = tmp_client["mac_pool"]
        device_client_macs_set[tmp_client["device_id"]] = set(tmp_client["client_macs"])

    child_dict: dict[str, list[str]] = {}
    root = client_belong_devices[0]
    for client in client_belong_devices:
        if not set(client["mac_pool"]).intersection(all_client_macs):
            root = client
        child_device_ids: set[str] = set()
        for device_id, device_mac_pool in site_device_macs.items():
            client_macs: set[str] = device_client_macs_set[device_id]
            if device_id != client["device_id"] and client_macs.intersection(
                set(device_mac_pool)
            ):
                if device_id in child_dict:
                    return None
                child_device_ids.add(device_id)

        if child_device_ids:
            child_dict.setdefault(client["device_id"], []).extend(child_device_ids)

    return traverse_device(child_dict, root["device_id"])


def test_find_last_device():
    client_mac = "EE:67:DB:5F:D3:75"

    client_belong_devices = [
        device for device in device_clients if client_mac in device["client_macs"]
    ]

    find_last_device_1(client_belong_devices=client_belong_devices)


def merge_indirect_clients(
    device_clients: [],
    merged_clients: dict[str, dict],
    keep_clients: [],
):
    cache_client_positon: dict = {}

    for client_mac, tmp_clients in groupby(keep_clients, key=itemgetter("mac_address")):
        client_belong_devices = [
            device for device in device_clients if client_mac in device["client_macs"]
        ]
        client_device_ids = [client["device_id"] for client in client_belong_devices]
        client_device_ids.sort()
        client_position_str = "_".join(client_device_ids)
        device_id = cache_client_positon.get(client_position_str)
        if not device_id:
            device_id = find_last_device(client_belong_devices)

        last_client = None
        if not device_id:
            last_client = max(tmp_clients, key=itemgetter("last_seen"))
        else:
            last_client = next(
                (
                    client
                    for client in tmp_clients
                    if client["connected_device_id"] == device_id
                    and client["mac_address"] == client_mac
                ),
                None,
            )
            cache_client_positon[client_position_str] = device_id
        if not last_client:
            continue
        if (client_mac not in merged_clients) or merged_clients[client_mac][
            "last_seen"
        ] < last_client["last_seen"]:
            merged_clients[client_mac] = last_client


merged_clients = {}

# print("=========START=========")
# start = datetime.datetime.now()
# print(start)
# merge_indirect_clients(device_clients, merged_clients, keep_clients)
# print("=========END=========")
# end = datetime.datetime.now()
# print(end)

# print("=========DURATION=========")
# print(end - start)

# export(file_name="merge_clients.json", data=merged_clients)
test_find_last_device()
