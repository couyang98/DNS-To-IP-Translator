# DNS-Translator

When starting this program, it will prompt you for a domain name.

Enter in the domain name in format <Domain>.<TopLevelDomain> eg. google.com

The program will craft a DNS message and query it to a Google DNS server for data. Once the data is received, the program will attempt to translate the data to a readable format.

The translation will be in format:
 - Header.ID: 16 bit id uniquely identify query message
 - Header.QR: Identify where its a query(0) or response(1)
 - Header.OPCODE:Specifies kind of query in this message
 - header.AA:
