from scapy.all import *
from scapy.layers.dns import DNS, DNSQR

import cbor2 as cbor

import pprint

import socket

import binascii


types = {0: 'ANY', 255: 'ALL',1: 'A', 2: 'NS', 3: 'MD', 4: 'MD', 5: 'CNAME',
         6: 'SOA', 7:  'MB',8: 'MG',9: 'MR',10: 'NULL',11: 'WKS',12: 'PTR',
         13: 'HINFO',14: 'MINFO',15: 'MX',16: 'TXT',17: 'RP',18: 'AFSDB',
         28: 'AAAA', 33: 'SRV',38: 'A6',39: 'DNAME'}

internal_name = {}
name_ref = {}

def insert_name (name):
    elm = name.split(".")

    print ("ADD ", name)

    if len(elm[-1]) == 0: # name ends with a . remove last elm
        elm.pop()

    elm.insert(0, None) # add to mark end to distguish between a.b.c and a.b.c.d

    tree = internal_name
    for e in elm[::-1]:
        if e in tree:
            tree = tree[e]
        else:
            empty_tree = {}
            tree[e] = empty_tree
            tree = empty_tree


def insert_rr_names(rr, nb_elm):
    for i in range(nb_elm):
        if rr[i].type in [5]: # CNAME
            insert_name(rr[i].rrname.decode())
            insert_name(rr[i].rdata.decode())
        elif rr[i].type in [1, 28]: # 1, AAAA
            insert_name(rr[i].rrname.decode())
        elif rr[i].type == 6: # SOA
            insert_name(rr[i].rrname.decode())
            insert_name(rr[i].mname.decode())           
            insert_name(rr[i].rname.decode())   
        elif rr[i].type ==  41: # OPT
            pass       
        else:
            print("need to be processed")
            rr[i].show()

name_ref_idx = 0

def to_name_ref(tree, index):
    global name_ref_idx

    if None in tree:
        return ""

    domain_name = ""

    stop = False
    while len (tree) == 1 and not stop:
        for k, v in tree.items(): # normally only 1 edement
            if k != None:
                domain_name = k + '.' + domain_name; 
                tree = v
            else:
                name_ref[name_ref_idx] = [domain_name, index]
                name_ref_idx += 1

                stop = True

    if len(tree) > 1: # several branches, have to split
        my_index = name_ref_idx
        name_ref[name_ref_idx] = [domain_name, index]
        name_ref_idx +=1
        for k, v in tree.items(): 
            if k != None:
                to_name_ref ({k: v}, my_index)
  

clean_name_ref = {}
def clean_pseudo_root():
    global  clean_name_ref, name_ref

    clean_name_ref = {}

    for k,v in name_ref.items():
        if k == 0 and v == ["ROOT.", 0]:
            pass
        elif k==0 and v[0].find("ROOT.") != -1:
            clean_name_ref[k] = v[0].replace(".ROOT.", "")
        elif v[1] == 0 and not 0 in clean_name_ref:
            clean_name_ref[k] = v[0]
            clean_name_ref[k] = clean_name_ref[k][:-1]
        else:
            clean_name_ref[k] = v
            clean_name_ref[k][0] = clean_name_ref[k][0][:-1]
        
    name_ref = clean_name_ref



x = {'com': {
            'google': {'cloud-dns-hostmaster': {None: {}}},
            'googledomains': {'ns-cloud-b1': {None: {}}}},
     'net': {'mozgcp': {'dataops': {'prod': {'ingestion-edge': {None: {},
                                             'prod': {None: {}}}}}}}}

#r = to_name_ref({'net': {'mozgcp': {'dataops': {'prod': {'ingestion-edge': {None: {}}}}}}}, 0)

#r = to_name_ref({'net': {'mozgcp': { 'net': {'mozgcp': {'dataops': {'prod': {'ingestion-edge': {None: {},
#                                            'prod': {None: {}}}}}}}}}}, 0)


#r = to_name_ref({'prod': {None: {}}}, 0)

ref_index = {}
def create_ref_index():
    for k, v in name_ref.items(): 
        name = ""
        while type(v) is list:
            name += v[0] + '.'
            v = name_ref[v[1]]
        name += v + '.'
        ref_index[name] = k          



def create_query (qr):
    qr.show()
    print ("looking for ", qr.qname.decode())
    pprint.pprint(ref_index)
    q = [qr.qtype, ref_index[qr.qname.decode()]]
    if qr.qclass != 1:
        q.append(qr.qclas)

    return q

def create_rr(rr, nb_elm):
    full_rr = []
    for i in range(nb_elm):
        if i < nb_elm - 1 :
            rr1 = binascii.hexlify(bytes(rr[i])).decode()
            rr2 = binascii.hexlify(bytes(rr[2])).decode()
            print (">",rr1)
            print ("-",rr2)

            print ("=", rr1.replace(rr2, ''))
        print(binascii.hexlify(bytes(rr[i])))
        if rr[i].type == 1:  #A 
            """ [Type, name(ref), IPv4 address, TTL, (CLASS) ]"""
            c_rr = [1, ref_index[rr[i].rrname.decode()], socket.inet_aton(rr[i].rdata), rr[i].ttl]
            print (c_rr)
        elif rr[i].type == 5: #CNAME
            """ [type, name(ref), cname(ref), ttl, (class)] """
            c_rr = [5, ref_index[rr[i].rrname.decode()], ref_index[rr[i].rdata.decode()], rr[i].ttl]
        elif rr[i].type == 6: #SOA
            """ [type, name(ref), cname(ref), ttl, (class)] """
            c_rr = [6, ref_index[rr[i].rrname.decode()], ref_index[rr[i].mname.decode()], 
            ref_index[rr[i].rname.decode()], rr[i].serial, rr[i].refresh, 
            rr[i].retry, rr[i].expire, rr[i].minimum, 
            rr[i].ttl]
        elif rr[i].type == 28: #AAAA
            """ [type, name(ref), IPv6 address, ttl, (class)] """
            c_rr = [28, ref_index[rr[i].rrname.decode()], socket.inet_pton(socket.AF_INET6,rr[i].rdata), rr[i].ttl]
        elif rr[i].type == 41: #?????
            """ [type, ] MUST BE ADDED"""
            c_rr = [41, 0, 0,0]
        else:
            print ("unkown type")
            0/0
        print (c_rr)
        full_rr.append(c_rr)
    
    return full_rr



    
dns_packets = rdpcap('dns.pcap')
for packet in dns_packets:
    if packet.haslayer(DNS):
        # print(packet[DNS].show())
        print ("*"*40)
        internal_name = {}

        dst = packet[IP].dst
        rec_type = packet[DNSQR].qtype

        Question = None
        Answer = None
        Authority = None
        Additional = None

        Flags = packet[DNS].qr << 15 | \
                packet[DNS].opcode <<  11 | \
                packet[DNS].aa << 10 |\
                packet[DNS].tc << 9 |\
                packet[DNS].rd << 8 |\
                packet[DNS].ra << 7 |\
                packet[DNS].z  << 6 |\
                packet[DNS].ad << 5 |\
                packet[DNS].cd << 4 |\
                packet[DNS].rcode 
                
        print (hex(Flags), bin(Flags))
        Header = [packet[DNS].id, Flags]

        packet[DNSQR].show()

        if packet[DNS].qr == 0:
            print ("query")
       
            """CBOR Query Formet: [QTYPE, QNAME, QCLASS]
            - QNAME is either of type string witch contains the
            domain name or an Interger to refer to name_ref.
            - if QCLASS == 1, it can be ommited.
            """

            Query = [packet[DNSQR].qtype, packet[DNSQR].qname.decode()]
            if packet[DNSQR].qclass != 1:
                Query.append(packet[DNSQR].qclass)

            Header.append(Query)
            print (Header)
            
            print ('Q,', len(bytes(packet[DNS])), ',',len (cbor.dumps(Header)), ',',
                        (len(bytes(packet[DNS]))- len (cbor.dumps(Header) )), ',', 
                        (len(bytes(packet[DNS]))- len (cbor.dumps(Header) ))/len(bytes(packet[DNS])),
                   ", ==, ", packet[DNSQR].qtype)
        else:
            packet[DNS].show()

            # first phase : look for all name in RR to create
            # the name_ref structure.

            insert_name(packet[DNSQR].qname.decode())

            if packet[DNS].an:
                insert_rr_names(packet[DNS].an, packet[DNS].ancount)

            if packet[DNS].ns:
                insert_rr_names(packet[DNS].ns, packet[DNS].nscount) 

            if packet[DNS].ar:
                insert_rr_names(packet[DNS].ar, packet[DNS].arcount)
 
            pprint.pprint (internal_name)

            to_name_ref({'ROOT': internal_name} , 0)

            pprint.pprint(name_ref)

            clean_pseudo_root()

            print ("NAME_REF to be sent", len(cbor.dumps(name_ref)))
            pprint.pprint(name_ref)

            create_ref_index()
            print ("Internal index")
            pprint.pprint(ref_index)

          
            Query = create_query(packet[DNSQR])
            print (Query)
        
            Answer = create_rr(packet[DNS].an, packet[DNS].ancount)
            Authority = create_rr(packet[DNS].ns, packet[DNS].nscount)
            Additionnal = create_rr(packet[DNS].ar, packet[DNS].arcount)

            Header.append (Query)
            Header.append (name_ref)
            Header.append (Answer)
            Header.append (Authority)
            Header.append (Additional)

            if Header[-1] in [None, []]: # remove Additional if empty
                del Header[-1]

            if Header[-1] in [None, []]: # remove Authority  if Add. and Auth. empty
                del Header[-1]
             

            pprint.pprint(Header)

            print ("R,", len(bytes(packet[DNS])), ',', len (cbor.dumps(Header)), ",", 
                   (len(bytes(packet[DNS]))- len (cbor.dumps(Header) )), ',', 
                   (len(bytes(packet[DNS]))- len (cbor.dumps(Header) ))/len(bytes(packet[DNS])),
                   ", ==, ", packet[DNSQR].qtype)


            internal_name = {}
            name_ref={}
            name_ref_idx = 0
            ref_index = {}

