import os
import time
import argparse
import subprocess


def list_interfaces():
    try:
        result = subprocess.run(["ip", "link", "show"], capture_output=True, text=True)
        output_lines = result.stdout.splitlines()

        interfaces = [line.split(":")[1].strip() for line in output_lines if "mtu" in line and not line.split(":")[1].strip().startswith(("lo", "docker"))]

        return interfaces
    except Exception as e:
        print(f"Error occurred while listing interfaces: {e}")
        return None



def get_interface_speed(interface):
    try:
        ethtool_result = subprocess.run(["ethtool", interface], capture_output=True, text=True)
        ethtool_output = ethtool_result.stdout.splitlines()

        for line in ethtool_output:
            if "Speed:" in line:
                speed = ''.join(filter(lambda x: x.isdigit() or x == '+', line.split(":")[1]))
                return speed
        return None
    except Exception as e:
        print(f"Error occurred while getting speed for interface {interface}: {e}")
        return None



def get_high_speed_interfaces(speed_threshold=10):
    interfaces = list_interfaces()  # Listeleyeceğimiz arayüzleri burada belirtiyoruz
    high_speed_interfaces = []

    for interface in interfaces:
        speed = get_interface_speed(interface)
        if speed:
            speed = int(speed)
            print(f"Speed for {interface}: {speed}")
            if speed >= speed_threshold:  # Belirlenen hız eşiğinden yüksek olanları bul
                high_speed_interfaces.append(interface)

    if high_speed_interfaces:
        for interface in high_speed_interfaces:
            pass
    else:
        print("No high-speed interfaces found.")    

    return high_speed_interfaces




def check_connection(interface):
    try:
        result = os.popen(f"ethtool {interface} | awk '/Link detected/{{print ($NF == \"yes\") ? 1 : 0}}'").read().strip()
        return int(result)
    except Exception as e:
        print(f"Error occurred while checking connection: {e}")
        return None
    


def send_to_dynatrace(interface, result):
    try:
        os.system(f'/opt/dynatrace/oneagent/agent/tools/dynatrace_ingest "int-test,interface-name={interface}" {result} -v')
        print(f"Sent result to Dynatrace for interface {interface}: {result}")
    except Exception as e:
        print(f"Error occurred while sending result to Dynatrace for interface {interface}: {e}")



def main(interfaces, interval):
    while True:
        try:
            for interface in interfaces:
                result = check_connection(interface)
                if result is not None:
                    print(f"Connection status for {interface}: {result}")
                    #send_to_dynatrace(interface, result)
                else:
                    print(f"Failed to retrieve connection status for {interface}.")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("Program terminated by user.")
            break



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="""Checking the status of interfaces and sending to Dynatrace
                                     If no parameter is provided, default interfaces will be the high-speed interfaces
                                     on that server. The code runs with a duration of 5 seconds Alternatively, you can
                                     run by providing these values.
                                     ----  python3 dynatrace-interface-alert.py ens33 ens37 --interval 4 --speed 10
                                     """)
    parser.add_argument("interfaces", nargs="*", help="Desired interfaces to be checked.")
    parser.add_argument("--interval", type=int, default=5, help="The interval for sending logs (e.g., 5).")
    parser.add_argument("--speed", type=int, default=10, help="Speed threshold (e.g., 10).")
    args = parser.parse_args()

    if not args.interfaces:
        args.interfaces = get_high_speed_interfaces(args.speed)


    main(args.interfaces, args.interval)

