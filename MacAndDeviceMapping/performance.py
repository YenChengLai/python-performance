import json
from operator import itemgetter
from itertools import groupby


f = open('device_clients.json')

device_clients = json.load(f)

f.close()

f = open('keep_clients.json')

keep_clients = json.load(f)

f.close()


def traverse_device(child_dict, device_id):
    if device_id not in child_dict:
        return device_id
    else:
        for child in child_dict[device_id]:
            return traverse_device(child_dict, child)
        return device_id


def find_last_device(client_belong_devices: []) -> str | None:
    print("visited")
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
            if set(client["client_macs"]).intersection(set(device_mac_pool)) and device_id != client["device_id"]:
                if device_id in child_dict:
                    return None
                child_device_ids.add(device_id)

        if child_device_ids:
            child_dict.setdefault(client["device_id"], []).extend(child_device_ids)

    return traverse_device(child_dict, root["device_id"])


def merge_indirect_clients(
    device_clients: [],
    merged_clients: dict[str, dict],
    keep_clients: [],
):
    cache_client_positon: dict = {}

    for client_mac, tmp_clients in groupby(keep_clients, key=itemgetter("mac_address")):
        client_belong_devices = [device for device in device_clients if client_mac in device["client_macs"]]
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
                    if client["connected_device_id"] == device_id and client["mac_address"] == client_mac
                ),
                None,
            )
            cache_client_positon[client_position_str] = device_id
        if not last_client:
            continue
        if (client_mac not in merged_clients) or merged_clients[client_mac]["last_seen"] < last_client["last_seen"]:
            merged_clients[client_mac] = last_client

merged_clients = {}

merge_indirect_clients(device_clients, merged_clients, keep_clients)

print(json.dumps(merged_clients))
