import time
import json
import ipaddress
import concurrent.futures
from functools import partial
from ioc_finder import find_iocs

class Test(): 
    def split_text(self, text):
        # Split text into chunks of 10kb. Add each 10k to array
        # In case e.g. 1.2.3.4 lands exactly on 20k boundary, it may be useful to overlap here.
        # (just shitty code to reduce chance of issues) while still going fast

        arr_one = []
        max_len = 2500 
        current_string = ""
        overlaps = 100 


        for i in range(0, len(text)):
            current_string += text[i]
            if len(current_string) > max_len:
                # Appending just in case even with overlaps
                if len(text) > i+overlaps:
                    current_string += text[i+1:i+overlaps]
                else:
                    current_string += text[i+1:]

                arr_one.append(current_string)
                current_string = ""

        if len(current_string) > 0:
            arr_one.append(current_string)

        #print("DATA:", arr_one)
        print("Strings:", len(arr_one))
        #exit()

        return arr_one 

    def _format_result(self, result):
        final_result = {}
        
        for res in result:
            for key, val in res.items():
                if key in final_result:
                    if isinstance(val, list) and len(val) > 0:
                        for i in val:
                            final_result[key].append(i)
                    elif isinstance(val, dict):
                        #print(key,":::",val)
                        if key in final_result:
                            if isinstance(val, dict):
                                for k,v in val.items():
                                    #print("k:",k,"v:",v)
                                    val[k].append(v)
                        #print(val)
                    #final_result[key].append([i for i in val if len(val) > 0])
                else:
                    final_result[key] = val

        return final_result

    def worker_function(self, inputdata):
        return find_iocs(inputdata["data"], included_ioc_types=inputdata["ioc_types"])

    def _with_concurency(self, array_of_strings, ioc_types):
        results = []
        #start = time.perf_counter()

        # Workers dont matter..?
        # What can we use instead? 

        results = []
        workers = 4
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit the find_iocs function for each string in the array
            futures = [executor.submit(
                find_iocs, 
                text=string, 
                included_ioc_types=ioc_types,
            ) for string in array_of_strings]

            # Wait for all tasks to complete
            concurrent.futures.wait(futures)

            # Retrieve the results if needed
            results = [future.result() for future in futures]
        
        return self._format_result(results)

    def parse_ioc_new(self, input_string, input_type="all"):
        if input_type == "":
            input_type = "all"

        #ioc_types = ["domains", "urls", "email_addresses", "ipv6s", "ipv4s", "ipv4_cidrs", "md5s", "sha256s", "sha1s", "cves"]
        ioc_types = ["domains", "urls", "email_addresses", "ipv4s", "ipv4_cidrs", "md5s", "sha256s", "sha1s", "cves"]

        # urls = 10.4 -> 9.1
        # emails = 10.4 -> 9.48
        # ipv6s = 10.4 -> 7.37
        # ipv4 cidrs = 10.4 -> 10.44

        if input_type == "" or input_type == "all":
            ioc_types = ioc_types
        else:
            input_type = input_type.split(",")
            for item in input_type:
                item = item.strip()

            ioc_types = input_type

        input_string = str(input_string)
        if len(input_string) > 10000:
            iocs = self._with_concurency(self.split_text(input_string), ioc_types=ioc_types)
        else:
            iocs = find_iocs(input_string, included_ioc_types=ioc_types)

        newarray = []
        for key, value in iocs.items():
            if input_type != "all":
                if key not in input_type:
                    continue
    
            if len(value) == 0:
                continue

            for item in value:
                # If in here: attack techniques. Shouldn't be 3 levels so no
                # recursion necessary
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if len(subvalue) == 0:
                            continue

                        for subitem in subvalue:
                            data = {
                                "data": subitem,
                                "data_type": "%s_%s" % (key[:-1], subkey),
                            }

                            if data not in newarray:
                                newarray.append(data)
                else:
                    data = {"data": item, "data_type": key[:-1]}
                    if data not in newarray:
                        newarray.append(data)

        # Reformatting IP
        i = -1
        for item in newarray:
            i += 1
            if "ip" not in item["data_type"]:
                continue

            newarray[i]["data_type"] = "ip"
            try:
                newarray[i]["is_private_ip"] = ipaddress.ip_address(item["data"]).is_private
            except Exception as e:
                print("Error parsing %s: %s" % (item["data"], e))

        try:
            newarray = json.dumps(newarray)
        except json.decoder.JSONDecodeError as e:
            return "Failed to parse IOC's: %s" % e

        return newarray

# Make it not run this for multithreads
if __name__ == "__main__":

    input_string = ""
    with open("testdata.txt", "r") as f:
        input_string = f.read()

    try:
        json_data = json.loads(input_string)
        # If array, loop
        if isinstance(json_data, list):
            cnt = 0
            start = time.perf_counter()
            for item in json_data:
                cnt += 1
                classdata = Test()

                ret = classdata.parse_ioc_new(item)
                #print("OUTPUT1: ", ret)

                #if cnt == 5:
                #    break

            print("Total time taken:", time.perf_counter()-start)
        else:
            classdata = Test()
            ret = classdata.parse_ioc_new(input_string)
            print("OUTPUT2: ", ret)
    except Exception as e:
        classdata = Test()
        ret = classdata.parse_ioc_new(json_data)
        print("OUTPUT3: ", ret)

