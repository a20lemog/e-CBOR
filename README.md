# e-CBOR description

e-CBOR (efficient Concise Binary Object Representation) is a method to optimize the size of DNS messages.

This method proposes a DNS format that is equivalent to and often more compact than the IETF format. It has proven that it is possible to use the RESTful paradigm to transport DNS requests or responses over the CoAP protocol.

CBOR is more flexible and new fields can be transported in the messages to extend DNS to new uses.


## e-CBOR implementation

- Install [Scapy 2.5.O](https://scapy.readthedocs.io/en/latest/installation.html)
- Install [wireshark 4.0.3](https://www.wireshark.org/download.html)
- Clone https://gitlab.imt-atlantique.fr/a20lemog/e-cbor.git repo where the implementation is located
  of a DNS request and response using the e-CBOR method.
- The pcap files of the different resource records to be added in the code can be found in the repo:
  https://gitlab.imt-atlantique.fr/a20lemog/e-cbor.git

### Future implementation
We will encapsulate the DNS messages encoded with e-CBOR in the CoAP protocol. 
