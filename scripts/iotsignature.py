from __future__ import annotations
import scapy.all as sc
import json
import requests
from bs4 import BeautifulSoup as bs4
import sys
print = lambda x:x

class Signature:
    def __init__(self, **kwargs):
        """
        DOCSTRING: this is the initialization function.
        parameters: name
        name: name of the signature.
        """
        try:
            # name is a string given by class user to identify the signature
            self.name = kwargs['name'] 
        
        except KeyError:
            self.name = "Unknown_device"

    def __convert_info(self, info):
        """
        DOSCTRING: this function will get a byte stream and convert it in to a decimal list
        return: decimal list corresponds to the byte stream
        """
        info_list = []
        for byte in info:
            info_list.append(byte)
        return info_list

    def __extract_signature(self, frame):
        """
        DOSCTRING: this function is the most important function of the SIGNATURE class
        DESCRIPTION: this funciton will go thorugh frame attributes and extract various capabilities in the frame. 
                    those capabilities are listed below and given a name. capabilities are identified by the ID. The ID can be 
                    found in the wireshark.

        return: a dictionary containing all the attributes
        """

        signature:dict[str: Signature] = {}

        # extracting hidden layers
        for i in range(5,100):
            try:
                temp = frame[i]
                if temp.ID == 45:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                    signature['ht'] = self.__convert_info(temp.info)
                elif temp.ID == 1:
                    signature['supported_rates'] = list(temp.rates)
                elif temp.ID == 50:
                    signature['ext_supported_rates'] = list(temp.rates)
                elif temp.ID == 59:
                    signature['operating_classes'] = self.__convert_info(temp.info)
                elif temp.ID == 127:
                    signature['extended'] = self.__convert_info(temp.info)
                elif temp.ID == 191 or temp.ID == 61:
                    signature['vht'] = self.__convert_info(temp.info)
                elif temp.ID == 255:
                    signature['he'] = self.__convert_info(temp.info)  
                elif temp.ID == 221:
                    signature['vendor_specific'] = self.__convert_info(temp.info)
                elif temp.ID == 107:
                    signature['interworking'] = self.__convert_info(temp.info)
                elif temp.ID == 70:
                    signature['RM enabled Capabilities'] = self.__convert_info(temp.info)
                
                
                ##################### PUT SPECIAL ATTENTION FOR THESE
                elif temp.ID == 114:
                    signature['Mesh ID'] = self.__convert_info(temp.info)
                
                
                elif temp.ID in [0,3, 127]:
                    # TAG ID 0 corresponds to SSID wildcard. (DEPENDS on the associated router, cannot take to signature)
                    # TAG ID 3 corresponds to CURRENT CHANNEL. (DEPENDS on the channel, cannot take it to signature)
                    pass
                else:
                    # incase of unidentified ID this will notify it
                    print("New ID found -----> ", temp.ID, "   source ---> ", frame.addr2)
            except IndexError:
                # the breaking condition is to find the ending layer of the frame
                break

        return signature

    def __r(self, probability, lambda_):
        """
        DOCSTRING: This function will convert p_i to r_i using the transformation T
        """
        alpha = 1-2/lambda_
        beta = (lambda_**2 - 4*lambda_ + 4)/(lambda_**2 - lambda_)

        if 0 <= probability <= 1:
            rarity_value = 1/(alpha - beta*(1-probability)) - 1/alpha
            return round(rarity_value, 5)
        else:
            return None

    def gamma(self,attribute, item1, item2, lambda_ = 5):
        """
        DOCSTRING: this function will give the rarity of finding two items
        """
        try:
            if isinstance(item1[0],list):
                ## attribute has multiple values
                attr = [item2 for val in item1 if val == item2]
                if attr: item1 = attr[0]
                else: item1 = item1[0] # use the fist attr value
                # print('attr {} -> {}'.format(item1,item2))
        except Exception:
            pass

        try:
            prob1 = self.stats[attribute][str(item1)]
        except KeyError:
            if attribute != 'Mesh ID':
                print(f"Statistical data not found item 1: check attr -> {attribute} -> key -> {item1}")
                print(self.name)
            prob1 = 0
        except AttributeError:
            print(f"Setup the statistics first")
            quit()

        try:
            prob2 = self.stats[attribute][str(item2)]
        except KeyError:
            if attribute != 'Mesh ID':
                print(f"Statistical data not found: check attr -> {attribute} -> key -> {item2}")
                print(self.name)
            prob2 = 0
        except AttributeError:
            print(f"Setup the statistics first")
            quit()


        joint_prob = prob1 * prob2

        return  self.__r(joint_prob, lambda_) 
    
    def __single_byte_similarity(self, byte1, byte2):
        """
        DOCSTRING: this function is used to calculate the similar bits in a given byte
        byte1, byte2: are integers [0, 255]
        return: the number of similar bits [0,8]
        """
        counter = 0
        number = (byte1 ^ byte2) ^ 255
        for i in range(8):
            if (number >> i) & 1:
                counter += 1
        return counter

    def ordered_bit_similarity(self, stream1, stream2):
        """
        DOCSTRING: this function will take two byte strings and return the bit similarity.
        IMPORTANT: this is NOT a SET SIMILARITY. The order of bits are considered. calculations are done using __single_byte_similarity()
                    function
        return: similarity index [0, 1]
        """
        similar_counter = 0
        
        # first get the stream with the maximum bytes. So we can address each byte
        # we can generate a Index Error
        # otherwire we will miss the bytes
        if len(stream1) >= len(stream2):
            a = stream1
            b = stream2
            total_stream_length = len(stream1) * 8
        else:
            a = stream2
            b = stream1
            total_stream_length = len(stream2) * 8
        
        try:
            for index, byte in enumerate(a):
                similar_counter += self.__single_byte_similarity(byte, b[index])
                
        except IndexError:
            pass

        return round(similar_counter / total_stream_length, 5)

    def jaccard_similarity(self, list_1, list_2):
        """
        DOSCTRING: this function will calculate the jaccard similarity for two lists
        IMPORTANT: the lists are considered as sets. ORDER is NOT considered
        return: the matching index, in range [0,1]
        """
        set_1 = set(list_1)
        set_2 = set(list_2)
        
        try:
            similarity = len(set_1.intersection(set_2)) / len(set_1.union(set_2))
            return round(similarity, 5)

        except ZeroDivisionError:
            return 1

    def __match_list(self, property_1, property_2, match_function):
        """
        DOCSTRING: this is also a very IMPORTANT function of Signature class. This is the main function used for matching two
                    attributes from two diffrenet signatures.
        property_1: one of the property to be matched
        property_2: other one of the property
        match_function  : the function must be used to get the matching
        """

        # identifiying if the properties are nested or not
        prop1_stat = any(isinstance(i, list) for i in property_1) # true if nested
        prop2_stat = any(isinstance(i, list) for i in property_2) # true if nested

        # if both are not nested we can directly use the match function
        if not prop1_stat and not prop2_stat:
            return match_function(property_1, property_2)

        # if one of them is nested we have to go through each element of the nested list
        elif prop1_stat and not prop2_stat:
            # we have to go through each element of the nested list
            temp = []
            for item in property_1:
                temp.append(match_function(item, property_2))
            return max(temp)
        
        elif not prop1_stat and prop2_stat:
            # we have to go through each element of the nested list
            temp = []
            for item in property_2:
                temp.append(match_function(property_1, item))
            return max(temp)

        else:
            # both are nested
            temp = []
            for item1 in property_1:
                for item2 in property_2:
                    temp.append(match_function(item1, item2))
            return max(temp)

    def sign(self, pcap_file, ignore_ssid = False):
        """
        DOCSTRING: this function will sign the empty signature using the PCAP dump given
        pcap_file:  1) location of the pcap file    OR 
                    2) Already read SCAPY PCAP file OR 
                    3) A single FRAME
        """

        try:
            
            if isinstance(pcap_file, str) or isinstance(pcap_file, sc.PacketList):
               
                if isinstance(pcap_file, str):
                     # First assuming that the given input is the location of the pcap file
                    # print(pcap_file)
                    cap = sc.rdpcap(pcap_file)
                else:
                    # else change the variable name
                    cap = pcap_file
                
                # NOTE: now we have to find the first frame wich has a SSID wildcard set
                for index_wild, frame in enumerate(cap):
                    if (frame.haslayer(sc.Dot11Elt) and frame[sc.Dot11Elt].ID == 0 and frame[sc.Dot11Elt].info == b'') or ignore_ssid:
                        self.signature = self.__extract_signature(cap[index_wild]) 
                        return True

                print("The given PCAP file does not contain a SSID wildcard frame")
                return False
                
            elif isinstance(pcap_file, sc.RadioTap):
                if (pcap_file.haslayer(sc.Dot11Elt) and pcap_file[sc.Dot11Elt].ID == 0 and pcap_file[sc.Dot11Elt].info == b'') or ignore_ssid:
                    self.signature = self.__extract_signature(pcap_file)
                    return True
                else:
                    print("The given frame is not SSID wildcard frame")
                    self.signature = None
                    return False
                
            
        except FileNotFoundError:
            print("File Not Found.")
    
    def __repr__(self):
        return str(self.name)

    def match(self, sign_frame, expand = False, weighted = True, lambda_ = 5,key_match='union'):
        """
        DOCSTRING: this is the main function used by the class users to match two signatures
        sign_frame: this could be,
                    1) a Signature object
                    2) a signature dictionary
                    3) a single frame, in this case we have to exract signature from the frame

        expand: if this is true, the function will output a descreptive score dictionary
        return: the matching scores
        """
        if isinstance(sign_frame, Signature):
            # in case of FRAME -> Signature() instance
            temp_signature = sign_frame.signature
            temp_name = sign_frame.name
        elif isinstance(sign_frame, dict):
            # in case of FRAME -> signature dictionary
            temp_signature = sign_frame
        else:
            # in case of FRAME -> single scapy frame
            temp_signature = self.__extract_signature(sign_frame) # extracting the signature of the frame
            
        try:

            # keys = np.unique(list(self.signature.keys()) + list(temp_signature.keys()))
            # keys = set(self.signature.keys()).union(temp_signature.keys())
            if key_match == 'union':
                keys = set(self.signature.keys()).union(temp_signature.keys())
            else:
                keys = set(self.signature.keys()).intersection(temp_signature.keys()) 
                        
            if not len(keys):
                print(f"CHECK {self.name} and {temp_name}")
                return 0, 0

            output_dictinoary = {}   # decreptive dictionary is this
            output_list = []         # matching scores will append to this (not descreptive)

            # this list contains the PROPERTY NAMES of the properties which must use BYTE SIMILARITY similarity check
            byte_check_attr_list = ['ht']

            for key in keys:
                
                try:
                    if weighted:
                        # get the weight (gamma)
                        if (key in self.signature) and (key in temp_signature):
                            weight = self.gamma(key, self.signature[key], temp_signature[key], lambda_= lambda_ )
                        elif key in self.signature:
                            weight = self.gamma(key, self.signature[key], 'null', lambda_= lambda_)
                        elif key in temp_signature:
                            weight = self.gamma(key, 'null', temp_signature[key], lambda_= lambda_)
                        else:
                            weight = self.gamma(key, 'null', 'null', lambda_= lambda_)
                    else:
                        weight = 1
                    
                    if key in byte_check_attr_list:
                        # match = self.__match_list(self.signature[key], temp_signature[key], match_function=self.__get_stream_byte_similarity)
                        match = self.__match_list(self.signature[key], temp_signature[key], match_function=self.jaccard_similarity)
                    else:
                        match = self.__match_list(self.signature[key], temp_signature[key], match_function=self.jaccard_similarity)

                    output_dictinoary[key] = (match, weight)
                    output_list.append((match, weight))

                except KeyError:
                    output_dictinoary[key] = (0, weight)
                    output_list.append((0, weight))

                    
            # calculating the weighted average
            total_sw = 0
            total_w = 0
            for match, weight in output_list:
                total_sw += match * weight
                total_w += weight
                
            weighted_avg = round(total_sw / total_w, 5)
            # print('weighted_avg {}'.format(weighted_avg))

            if expand:
                return output_dictinoary, weighted_avg
            else:
                return output_list, weighted_avg
        
        except AttributeError:
            # attribute error occures because not signed before
            print("First sign the signature")
        except ZeroDivisionError:
            print(self.signature)
            print(temp_signature)
            sys.exit()

   ### new match function

    def match_wp(
            self,
            sign_frame: Signature,
            expand = False,
            weighted = True,
            lambda_ = 5,
            key_match = 'union',
            signatures_wt:Signature = None
        ):

        if isinstance(sign_frame, Signature):
            temp_signature = sign_frame.signature
            temp_name = sign_frame.name
        elif isinstance(sign_frame, dict):
            temp_signature = sign_frame
        else:
            temp_signature = self.__extract_signature(sign_frame) # extracting the signature of the frame
            
        try:
            if key_match == 'union':
                keys = set(self.signature.keys()).union(temp_signature.keys())
            else:
                keys = set(self.signature.keys()).intersection(temp_signature.keys()) 
                        
            if not len(keys):
                print(f"CHECK {self.name} and {temp_name}")
                return 0, 0

            output_dictinoary = {}   # decreptive dictionary is this
            output_list = []         # matching scores will append to this (not descreptive)

            total_sw,total_w = 0,0
            # print(keys)
            for key in keys:
                try:
                    if (key in self.signature) and (key in temp_signature):
                        weight = self.gamma(key, self.signature[key], temp_signature[key], lambda_= lambda_ )
                        match = self.__match_list(self.signature[key], temp_signature[key], match_function=self.jaccard_similarity)
                        
                        weight = weight*signatures_wt.signature[key]['weight'] 
                        total_sw +=(weight*match)
                        total_w += weight
                    elif key in self.signature:
                        weight = self.gamma(key, self.signature[key], 'null', lambda_= lambda_)
                        match = 0
                        weight = weight*signatures_wt.signature[key]['weight'] 
                        total_sw +=(weight*match)
                        total_w += weight 
                        # total_w += weight*signatures_wt.signature[key]['weight'] # multiply by probability of occurence
                        # print('w1 {}'.format(signatures_wt.signature[key]['weight']))
                        # print('w {}'.format(weight))

                    elif key in temp_signature:
                        weight = self.gamma(key, 'null', temp_signature[key], lambda_= lambda_)
                        weight = weight*signatures_wt.signature[key]['weight']
                        match = 0
                        total_sw +=(weight*match)
                        total_w += weight
                    else:
                        weight = self.gamma(key, 'null', 'null', lambda_= lambda_)
                        weight = weight*signatures_wt.signature[key]['weight']
                        match = 0
                        total_sw +=(weight*match)
                        total_w += weight

                        
                    if match > 0.0001:
                        match, weight = (0,0)
                    output_dictinoary[key] = (match, weight)
                    output_list.append((match, weight))

                except KeyError as e:
                    # print('key erro {}'.format(e))
                    output_dictinoary[key] = (0, weight)
                    output_list.append((0, weight))
                
            # print('total_sw {}'.format(total_sw))
            # print('total_w {}'.format(total_w))
            weighted_avg = round(total_sw / total_w, 5)
            # print('weighted_avg {}'.format(weighted_avg))

            if expand:
                return output_dictinoary, weighted_avg
            else:
                return output_list, weighted_avg
        
        except AttributeError  as e:
            print(sign_frame.name)
            print(signatures_wt.name)
            print('match_wp - >{}'.format(e))
        except ZeroDivisionError:
            print(self.signature)
            print(temp_signature)
            sys.exit()


    def __mod__(self, other):
        """
        DOCSTRING: this function will return a match percentage. should give frame 
        """
        _, match = self.match(other)
        return match

    def load(self, location):
        """
        DOCSTRING: this function will load a premade signature from a file
        location: file path of the signature
        """
        with open(location, 'r') as input_file:
             temp = json.load(input_file)

        self.name = list(temp.keys())[0]
        self.signature = temp[self.name]

    def store(self, location):
        """
        DOCSTRING: this function will store the signature stores in self.signature
        """
        try:
            with open(location, 'w') as output_file:
                json.dump({self.name: self.signature}, output_file)
            
        except AttributeError:
            print("First sign the signature using sign function")


####################################################################################################

class SignatureBase:
    def __init__(self, stats, signs:list[Signature] = [], path:str = '', **kwargs):
        """
        IMPORTANT: two keys can be given
                    1) signs: a list with Signature object inside it
                    2) path: path to the database file
        """
        if isinstance(stats, dict):
            self.stats = stats
        elif isinstance(stats, str):
            with open(stats, 'r') as input_file:
                self.stats = json.load(input_file)

        self.signatures: list[Signature] = signs
        self.db_path:str = path

        def load_kwarg(key, attr_name):
            if key in kwargs:
                self.__dict__[attr_name] = kwargs[key]


        load_kwarg('signs', 'signatures')
        load_kwarg('path', 'db_path')

        # adding signatues with probability of occurence for each sig attribute
        if 'path2' in kwargs:
            self.db2_path = kwargs['path2']
            self.signatures_wp = []
            self.weighted_database = {}
        else:
            self.db2_path = ''

        self.database = {}
        
        # if a set of signatures are given, fill the databse with those signatures
        if len(self.signatures):
            for signature in self.signatures:
                self.database[signature.name] = signature.signature
    
    def load(self, primary_path = None):
        """
        DOSCTRING: this function will load a database saved in a file.
        primary_path: this is the path of the loading file. If it is not given database path must exist
        """
        if primary_path:
            path = primary_path
        elif len(self.db_path):
            path = self.db_path
        else:
            print("set the db path")
            return 0

        with open(path, 'r') as input_file:
            self.database = json.load(input_file)
        
        self.signatures = []
        for key in self.database:
            temp_signature = Signature(name = key)
            temp_signature.stats = self.stats
            temp_signature.signature = self.database[key]
            
            self.signatures.append(temp_signature)

        if len(self.db2_path):
            with open(self.db2_path,'r') as input_f:
                self.weighted_database = json.load(input_f)
            
            self.signatures_wp = []
            for key in self.weighted_database:
                temp_signature = Signature(name = key)
                temp_signature.stats = self.stats
                temp_signature.signature = self.weighted_database[key]
                
                self.signatures_wp.append(temp_signature)

   
                 
    def store(self, primary_path = None):
        """
        DOSCTRING: this function will store the database to a file.
        primary_path: this is the path of the loading file. If it is not given database path must exist
        """
        if primary_path:
            path = primary_path
        elif len(self.db_path):
            path = self.db_path
        else:
            print("set the db path")
            return 0

        with open(path, 'w') as output_file:
            json.dump(self.database, output_file)
                
    def add(self, signatures:list[Signature]):
        """
        DOSCTRING: this function is used to append abother singature to the database
        IMPORTANT: must optimise this function. takes too much time
        """
        try:
            for signature in signatures:
                self.signatures.append(signature)
                self.database[signature.name] = signature.signature
                
        except TypeError:
            self.signatures.append(signatures)
            self.database[signatures.name] = signatures.signature
    
    def explore(self, pcap_file, threshold = 0.85) -> list:
        """
        DOSCTRING: this function is used to explore a pcap file with the databse
        pcap_file: this is a scapy pcap.list object
        threshold: this is the matching threshold. 0.85 is expiremental. mut be in range [0, 1]
        return: a list of matches
        """
        matches = []
        
        for index, frame in enumerate(pcap_file):
            if frame.haslayer(sc.Dot11):
                if frame.type == 0 and frame.subtype == 4:
                    # now this is a probe request frame
                    
                    # check each request with all the element in the database
                    max_match = 0
                    max_match_name = ""
                    
                    for signature in self.signatures:
                        _, avg = signature.match(frame)
                        if avg > max_match:
                            max_match = avg
                            max_match_name = signature.name
                    
                    # if it has a matching average abouve 0.6 append it
                    if max_match > threshold:
                        matches.append([index + 1, frame.addr2, max_match, max_match_name])
                    
        
        return matches

    def get(self, key: str) -> Signature:
        """
        DOSCTRING: this function is used to get the Signature object by signature name
        key: the signature name
        return: a Signature object
        """
        try:
            signature = Signature(name = key)
            signature.stats = self.stats
            signature.signature = self.database[key]
            return signature

        except KeyError:
            print("BAD key!!!")
            return None
        
    def get_ws(self, key: str) -> Signature:
        try:
            signature_w = Signature(name = key)
            signature_w.stats = self.stats
            signature_w.signature = self.weighted_database[key]
            return signature_w

        except KeyError:
            print("BAD key!!!")
            return None


    def predict(self, signature, lambda_ = 2.1, verbose = False,key_match='union',probability_occ = False):

        """
        DOCSTRING: this function will return the best machings from the database
        return: best maching signatures
        """
        matches = []
        for index,temp_signature in enumerate(self.signatures):
            if probability_occ:
                # print(self.signatures_wp[index].name)
                _, score = temp_signature.match_wp(signature, lambda_ = lambda_,key_match= key_match,signatures_wt=self.signatures_wp[index])

            else:
                _, score = temp_signature.match(signature, lambda_ = lambda_,key_match= key_match)
            
            matches.append([temp_signature.name, score])

        matches.sort(key = lambda x: x[1], reverse = True)

        if verbose:
            # return first 3 maching signatures
            return matches[:3]
        else:
            return matches[0][0]

###############################################################################################

class MacUtilities:
    def __init__(self, mac_database): # figure out vendor from MAC
        """
        mac_database: the path to the mac database JSON file (required)
        """
        self.mac_database = mac_database #mac_data.json 

        # the below code is for the API used to get OUI information
        self.key_counter = 0 # this counter is used in get_vendor() function below
        # these are API keys for the online free API
        self.keys = [
                        'at_pyiHQtMHLDF0iPwLLfEID617Sh6Dz',
                        'at_TF1FfDBFZikaC11POTvxz8NX8veIO',
                        'at_XTYR1dOo0QINQj6nkfiuS4B7WUeqD',
                        'at_uxT93INrHtEV1xcux9RyrlfZK0x6W'
                    ]
        
        with open(self.mac_database, 'r') as mac_file:
            self.vendors = json.load(mac_file)
    
    def is_local(self, mac):
        """
        DOSCTRING: this function will tell if the mac address is localized
        """
        mac = mac.split(":") # split by : to get all the seperate octets
        # print(' mac from MacUtlis {}'.format(mac))
        o1 = int(mac[0], 16)

        return o1 & 2 > 0


    def is_multicast(self, mac):
        """
        DOCSTRING: this function will tell if the mac address is multicast
        """
        mac = mac.split(":") # split by : to get all the seperate octets
        o1 = int(mac[0], 16)

        return o1 & 1 > 0

    def is_random(self, mac):
        """
        DOCSTRING: this function will tell if the OUI is randomized
        """
        return self.is_local(mac) and not self.is_multicast(mac)
    

    def get_vendor(self, mac_address):
        """
        DOSCTRING: this function will return the name of the vendor of the MAC address using OUI infomation
        mac_address: the FULL MAC address of the device
        return: a STRING
        """
        # first of all check if the address is randomized. If yes then say just Randomized (Nothing else to do)

        if '?' in mac_address:
            mac_address = mac_address.split('?')[0]
            
        if not self.is_random(mac_address):
            
            # then check the JSON file (localy saved information) for the OUI information
            if mac_address[:-9] in self.vendors:
                return self.vendors[mac_address[:-9]]

            # then use the unlimited free API (Not guarenteed to have all the OUI information, some of them are missing) 
            else:
                # print('finding form lookup table')
                data = {'oui': mac_address[:-9]}
                # print('data')

                r = requests.post("https://www.cleancss.com/mac-lookup/index.php", data=data)

                r = bs4(r.text)
                try:
                    st_list = r.p.find_all('strong')
                    vendor = st_list[-1].text
                    self.vendors[mac_address[:-9]] = vendor
                    return vendor
                
                except IndexError:
                    # Index error occure when the above free api could not find a result
                    while True:
                        try:
                            url = f"https://api.macaddress.io/v1?apiKey={self.keys[self.key_counter]}&output=json&search={mac_address}"
                            r = requests.get(url)
                            result = json.loads(r.text)['vendorDetails']['companyName']
                            self.vendors[mac_address[:-9]] = result

                            return result
                        
                        except KeyError:
                            # key error occure when the api returns nothing. usually this happens because no of attempt are over runned
                            self.key_counter += 1
                            if self.key_counter >= len(self.keys):
                                print(f"WARNING: could not find OUI information for MAC address {mac_address}")
                                return None

        else:
            return "Randomized"
   
    def store(self):
        """
        DOCTRING: this function will store the information in self.vendors variable to a file
        """
        # write new mac json file
        with open(self.mac_database, 'w') as vendor_file:
            json.dump(self.vendors, vendor_file)
    
    def get_remaining_api_counter(self):
        """
        DOCSTRING: this function will tell how much attemts left on online API
        return: number of attemts
        """
        counter = 0
        for key in self.keys:
            r = requests.get(f'https://api.macaddress.io/v1/credits?apiKey={key}')
            counter += int(r.text)
        return counter
    