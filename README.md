# DNS-Translator

When starting this program, it will prompt you for a domain name.

Enter in the domain name in format <Domain>.<TopLevelDomain> eg. amazon.com

The program will craft a DNS message and query it to a Google DNS server for data. Once the data is received, the program will attempt to translate the data to a readable format.

The translation will be in format:
* Header *
 - header.ID: 16 bit id uniquely identify query message.
 - header.QR: Identify where its a query(0) or response(1).
 - header.OPCODE:Specifies kind of query in this message.
 - header.AA: Indicates if the responding server is authoritatively responsible for the domain name in question. (1) indicates authority and (0) indicates non-authority.
 - header.TC: Indicates if response message was truncated due to the message being too large. (1) indicates truncation and (0) indicates non-truncation
 - header.RD: Indicates if recursive resolution was requested during query. 
 - header.RA: Indicates if recursive resolution was used(1) or not(0). (0) might also indicate that a server does not support it.
 - header.Z: Three reserved bits always 0.
 - header.RCODE: Indicates if query was successful or identifies an error.
 - header.QDCOUNT: Number of questions in the message.
 - header.ANCOUNT: Number of answers in the message.
 - header.NSCOUNT: Number of resource records authority section of message.
 - heeader.ARCOUNT: Number of resource records in additional section of message.
**Question**
 - question.QNAME: The domain name that is being queried.
 - question.QTYPE: Specifies the type of query.
 - question.QCLASS: Specifies the class of the query.
**Answer**
 - answer.NAME: The domain name that is being queried.
 - answer.TYPE: Specifies the type of data being sent to RDATA.
 - answer.CLASS: Specifies the class of data in RDATA.
 - answer.TTL: -	Time interval (in seconds) that the RR may be cached before considered outdated. 
 - answer.RDLENGTH: Length of the RDATA.
 - answer.RDATA: The data response for the query request.
