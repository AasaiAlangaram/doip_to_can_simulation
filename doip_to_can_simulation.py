import asyncio
import struct


# Constants
DOIP_HEADER_FORMAT = ">BBHII"  # Protocol Version, Inverse Protocol Version, Payload Type, Payload Length
DIAGNOSTIC_PAYLOAD_FORMAT = ">HHBHB"  # Target Address, Source Address, Service ID, Data Identifier (16-bit)
CAN_ID_REQUEST = 0x600
CAN_ID_RESPONSE = 0x601
DOOR_LOGICAL_ADDRESS = 0x0205
DIAGNOSTIC_SERVICE_ID = 0x22
DATA_IDENTIFIER = 0xF190


async def tester():
    print("Tester: Sending diagnostic request to GW")
    request = create_diagnostic_request(DOOR_LOGICAL_ADDRESS, DIAGNOSTIC_SERVICE_ID, DATA_IDENTIFIER)
    await gateway(request)


def create_diagnostic_request(logical_address, service_id, data_identifier):
    # Create a diagnostic request
    packet = struct.pack(">HBBH", logical_address, service_id, 0x00, data_identifier)
    return packet


async def gateway(request):
    print("GW: Received diagnostic request from Tester")
    logical_address, service_id, _, data_identifier = struct.unpack(">HBBH", request)

    if logical_address == DOOR_LOGICAL_ADDRESS:
        print(f"GW: Mapping request to ECU with logical address: {hex(logical_address)}")
        can_request = create_can_message(CAN_ID_REQUEST, service_id, data_identifier)
        can_response = await door_ecu(can_request)
        await gateway_response(can_response)
    else:
        print("GW: Invalid logical address")


def create_can_message(can_id, service_id, data_identifier):
    # Create a CAN message
    packet = struct.pack(">HBH", can_id, service_id, data_identifier)
    return packet


async def door_ecu(request):
    print("Door ECU: Received request from GW")
    can_id, service_id, data_identifier = struct.unpack(">HBH", request)

    if can_id == CAN_ID_REQUEST:
        print(f"Door ECU: Processing request for service ID: {hex(service_id)} and Data ID: {hex(data_identifier)}")
        response_data = b'1HGBH41JXMN109186'  # VIN data
        can_response = create_can_message(CAN_ID_RESPONSE, service_id, data_identifier) + response_data
        return can_response
    else:
        print("Door ECU: Invalid CAN ID")
        return None


async def gateway_response(response):
    if response:
        print("GW: Received response from ECU")
        can_id, service_id, data_identifier, response_data = struct.unpack(">HBH17s", response)

        if can_id == CAN_ID_RESPONSE:
            print(f"GW: Sending response to Tester: {response_data.decode()}")
            await tester_response(response_data)
        else:
            print("GW: Invalid CAN ID")


async def tester_response(response_data):
    print(f"Tester: Received response from GW: {response_data.decode()}")


# Main function
async def main():
    await tester()


if __name__ == "__main__":
    asyncio.run(main())
